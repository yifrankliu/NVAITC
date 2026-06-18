import torch
import torch.nn as nn
from torch.distributions import MultivariateNormal
from torch.distributions import Categorical

# --- making the sustain-lc submodule importable (repo-relative, move-safe) ---
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "external" / "sustain-lc"))
# ---------------------------------------------------------------------------
from ca_ppo import RolloutBuffer

################################## set device ##################################
print("============================================================================================")
# set device to cpu or cuda
device = torch.device('cpu')
if(torch.cuda.is_available()):
    device = torch.device('cuda:0')
    torch.cuda.empty_cache()
    print("Device set to : " + str(torch.cuda.get_device_name(device)))
else:
    print("Device set to : cpu")
print("============================================================================================")

################################## PPO Policy ##################################
# rolloutbuffer class directly imported from ca_ppo
class UnifiedActorCritic(nn.Module):
    def __init__(self, state_dim, cdu_action_dim, ct_action_dim, cdu_action_std_init):
        super().__init__()
        # define cdu_action, continuous actor, discrete actor, and critic
        self.cdu_action_dim = cdu_action_dim
        self.ct_action_dim = ct_action_dim

        # since unified algorithm considers both the continuous cabinet-side actions
        # and the discrete ct-side actions at the same time, we need to creat action_var no matter what
        self.cdu_action_var = torch.full((cdu_action_dim,), cdu_action_std_init * cdu_action_std_init).to(device)

        # creating two actors-critics, one each for cdu and ct
        # we treat continuous actions with Tanh, since scaled perfectly between [-1, 1]
        # for Tan's asymptotic behavior
        self.cdu_actor = nn.Sequential(
                            nn.Linear(state_dim, 64),
                            nn.Tanh(),
                            nn.Linear(64, 64),
                            nn.Tanh(),
                            nn.Linear(64, cdu_action_dim),
                            nn.Tanh()
                        )
        
        # ct actor
        self.ct_actor = nn.Sequential(
                            nn.Linear(state_dim, 64),
                            nn.Tanh(),
                            nn.Linear(64, 64),
                            nn.Tanh(),
                            nn.Linear(64, ct_action_dim),
                            nn.Softmax(dim=-1)
                        )
        
        # critic
        self.critic = nn.Sequential(
                        nn.Linear(state_dim, 64),
                        nn.Tanh(),
                        nn.Linear(64, 64),
                        nn.Tanh(),
                        nn.Linear(64, 1)
                    )
        
    # input would be both continuous and discrete, so always create action_var
    def set_action_std(self, new_cdu_action_std):
        self.cdu_action_var = torch.full((self.cdu_action_dim,), new_cdu_action_std * new_cdu_action_std).to(device)

    # guardrail
    def forward(self):
        raise NotImplementedError
    
    def act(self, state, return_imp_wts = False):

        # cdu (continuous) act imp:
        cdu_action_mean = self.cdu_actor(state)
        cdu_cov_mat = torch.diag(self.cdu_action_var)
        cdu_dist = MultivariateNormal(cdu_action_mean, cdu_cov_mat)

        # ct (discrete) act imp:
        ct_action_probs = self.ct_actor(state)
        ct_dist = Categorical(ct_action_probs)

        # take action & criticize
        cdu_action = cdu_dist.sample()
        ct_action = ct_dist.sample()
        cdu_action_logprob = cdu_dist.log_prob(cdu_action)
        ct_action_logprob = ct_dist.log_prob(ct_action)
        state_val = self.critic(state)

        # skip return important weights because not benchmarking multihead

        return cdu_action.detach(), ct_action.detach(), cdu_action_logprob.detach(), ct_action_logprob.detach(), state_val.detach()
        
    def evaluate(self, state, cdu_action, ct_action):        

        # cdu (continuous) evaluation imp:
        cdu_action_mean = self.cdu_actor(state)
        cdu_action_var = self.cdu_action_var.expand_as(cdu_action_mean)
        cdu_cov_mat = torch.diag_embed(cdu_action_var).to(device)
        cdu_dist = MultivariateNormal(cdu_action_mean, cdu_cov_mat)

        # ct (discrete) evaluation imp:
        ct_action_probs = self.ct_actor(state)
        ct_dist = Categorical(ct_action_probs)

        # logprobs, entropy, and critic for both cdu & ct
        cdu_action_logprobs = cdu_dist.log_prob(cdu_action)
        ct_action_logprobs = ct_dist.log_prob(ct_action)
        cdu_dist_entropy = cdu_dist.entropy()
        ct_dist_entropy = ct_dist.entropy()
        state_values = self.critic(state)

        return cdu_action_logprobs, ct_action_logprobs, cdu_dist_entropy, ct_dist_entropy, state_values
    
class Unified_PPO:
    def __init__(self, state_dim, cdu_action_dim, ct_action_dim, num_centralized_actions,
                 lr_cdu_actor = 0.0003, lr_ct_actor = 0.0003, lr_critic = 0.001, gamma = 0.80,
                 K_epochs = 50, eps_clip = 0.2,
                 cdu_action_std_init = 0.6):
        
        # again, since one agent is making both the continuous cdu decisions
        # and the discrete ct decisions, both continuous & discrete are implemented
        self.num_centralized_actions = num_centralized_actions
        self.cdu_action_std = cdu_action_std_init

        self.gamma = gamma
        self.eps_clip = eps_clip
        self.K_epochs = K_epochs

        # implementing buffer for two types of actions
        self.buffer_dict = {}
        self.buffer_dict['cdu_action'] = RolloutBuffer()
        self.buffer_dict['ct_action'] = RolloutBuffer()

        # instantiating actorcritic & imp optimizer
        self.policy = UnifiedActorCritic(state_dim, cdu_action_dim, ct_action_dim, cdu_action_std_init).to(device)
        self.optimizer = torch.optim.Adam([
                        {'params': self.policy.cdu_actor.parameters(), 'lr': lr_cdu_actor},
                        {'params': self.policy.ct_actor.parameters(), 'lr': lr_ct_actor},
                        {'params': self.policy.critic.parameters(), 'lr': lr_critic}
        ])

        self.policy_old = UnifiedActorCritic(state_dim, cdu_action_dim, ct_action_dim, cdu_action_std_init).to(device)
        self.policy_old.load_state_dict(self.policy.state_dict())

        self.MseLoss = nn.MSELoss()

        self.next_state = None

    def set_action_std(self, new_cdu_action_std):
        
        # cdu continuous imp:
        self.cdu_action_std = new_cdu_action_std
        self.policy.set_action_std(new_cdu_action_std)
        self.policy_old.set_action_std(new_cdu_action_std)
    
    def decay_action_std(self, cdu_action_std_decay_rate, min_cdu_action_std):
        self.cdu_action_std = self.cdu_action_std - cdu_action_std_decay_rate
        self.cdu_action_std = round(self.cdu_action_std, 4)
        if (self.cdu_action_std <= min_cdu_action_std):
            self.cdu_action_std = min_cdu_action_std
            print("setting cdu actor output action_std to min_cdu_action_std : ", self.cdu_action_std)
        else:
            print("setting cdu actor output action_std to : ", self.cdu_action_std)
        self.set_action_std(self.cdu_action_std)
    
    def select_action(self, states, return_imp_wts = False):

        with torch.no_grad():
            states = torch.FloatTensor(states).to(device)

            # again, here we ignore return_imp_wts alternative for easier implementation
            cdu_actions, ct_actions, cdu_action_logprobs, ct_action_logprobs, state_vals = self.policy_old.act(states, return_imp_wts = False)
        
        if self.num_centralized_actions == 1:
            states, cdu_actions, ct_actions, cdu_action_logprobs, ct_action_logprobs, state_vals = states.unsqueeze(0), cdu_actions.unsqueeze(0), ct_actions.unsqueeze(0), cdu_action_logprobs.unsqueeze(0), ct_action_logprobs.unsqueeze(0), state_vals.unsqueeze(0) 

        for state, cdu_action, ct_action, cdu_action_logprob, ct_action_logprob, state_val in zip(states, cdu_actions, ct_actions, cdu_action_logprobs, ct_action_logprobs, state_vals):
            self.buffer_dict['cdu_action'].states.append(state)
            self.buffer_dict['cdu_action'].actions.append(cdu_action)
            self.buffer_dict['cdu_action'].logprobs.append(cdu_action_logprob)
            self.buffer_dict['cdu_action'].state_values.append(state_val)  

            self.buffer_dict['ct_action'].states.append(state)
            self.buffer_dict['ct_action'].actions.append(ct_action)
            self.buffer_dict['ct_action'].logprobs.append(ct_action_logprob)
            self.buffer_dict['ct_action'].state_values.append(state_val)  
            
        # ignored cases when wts=true and when num_centralized_actions == 1 because
        # cases do not exist for this baseline test

        return cdu_actions.reshape(5, 5).detach().cpu().numpy(), ct_actions.item()
    
    def prepare_update_data(self,):

        next_state = torch.FloatTensor(self.next_state).to(device)
        with torch.no_grad():
            next_state_value = self.policy_old.critic(next_state).detach()
        
        # action buffer loops, again split into cdu & ct
        cdu_mc_returns = []
        ct_mc_returns = []
        cdu_discounted_reward = next_state_value
        ct_discounted_reward = next_state_value

        for cdu_reward, is_terminal in zip(reversed(self.buffer_dict['cdu_action'].rewards), reversed(self.buffer_dict['cdu_action'].is_terminals)):
            if is_terminal:
                    cdu_discounted_reward = 0
            cdu_discounted_reward = cdu_reward + (self.gamma * cdu_discounted_reward)
            cdu_mc_returns.insert(0, cdu_discounted_reward)
        
        for ct_reward, is_terminal in zip(reversed(self.buffer_dict['ct_action'].rewards), reversed(self.buffer_dict['ct_action'].is_terminals)):
            if is_terminal:
                    ct_discounted_reward = 0
            ct_discounted_reward = ct_reward + (self.gamma * ct_discounted_reward)
            ct_mc_returns.insert(0, ct_discounted_reward)
    
        # Normalization
        cdu_mc_returns = torch.tensor(cdu_mc_returns, dtype=torch.float32).to(device)
        cdu_mc_returns = (cdu_mc_returns - cdu_mc_returns.mean()) / (cdu_mc_returns.std() + 1e-7)
        ct_mc_returns = torch.tensor(ct_mc_returns, dtype=torch.float32).to(device)
        ct_mc_returns = (ct_mc_returns - ct_mc_returns.mean()) / (ct_mc_returns.std() + 1e-7)
        
        # States are the same for both cdu & ct
        old_states = torch.squeeze(torch.stack(self.buffer_dict['cdu_action'].states, dim=0)).detach().to(device)
        cdu_old_actions = torch.squeeze(torch.stack(self.buffer_dict['cdu_action'].actions, dim=0)).detach().to(device)
        cdu_old_logprobs = torch.squeeze(torch.stack(self.buffer_dict['cdu_action'].logprobs, dim=0)).detach().to(device)
        ct_old_actions = torch.squeeze(torch.stack(self.buffer_dict['ct_action'].actions, dim=0)).detach().to(device)
        ct_old_logprobs = torch.squeeze(torch.stack(self.buffer_dict['ct_action'].logprobs, dim=0)).detach().to(device)
        old_state_values = torch.squeeze(torch.stack(self.buffer_dict['cdu_action'].state_values, dim=0)).detach().to(device)
            
        # num_centralized_actions replaced by continuous cdu and discrete ct
        cdu_advantages = cdu_mc_returns.detach() - old_state_values.detach()
        ct_advantages = ct_mc_returns.detach() - old_state_values.detach()

        # packing step is removed because split cdu & ct

        # now we have all the data we need to update the policy
        # return the variables to the update method
        return cdu_mc_returns, ct_mc_returns, cdu_discounted_reward, ct_discounted_reward, old_states, cdu_old_actions, ct_old_actions, cdu_old_logprobs, ct_old_logprobs, old_state_values, cdu_advantages, ct_advantages
    
    def update(self):

        # Monte Carlo estimation
        cdu_mc_returns, ct_mc_returns, cdu_discounted_reward, ct_discounted_reward, old_states, cdu_old_actions, ct_old_actions, cdu_old_logprobs, ct_old_logprobs, old_state_values, cdu_advantages, ct_advantages = self.prepare_update_data()

        # Optimize policy for K epochs
        for _ in range(self.K_epochs):

            # Shuffle in data
            indices = torch.randperm(old_states.size(0))
            old_states = old_states[indices]
            cdu_old_actions = cdu_old_actions[indices]
            ct_old_actions = ct_old_actions[indices]
            cdu_old_logprobs = cdu_old_logprobs[indices]
            ct_old_logprobs = ct_old_logprobs[indices]
            cdu_advantages = cdu_advantages[indices]
            ct_advantages = ct_advantages[indices]
            cdu_mc_returns = cdu_mc_returns[indices]
            ct_mc_returns = ct_mc_returns[indices]

            # Split data into minibatches
            minibatch_size = 32
            num_minibatches = old_states.size(0) // minibatch_size
            for i in range(num_minibatches):
                start = i * minibatch_size
                end = (i + 1) * minibatch_size

                #Get minibatch data
                minibatch_old_states = old_states[start:end]
                minibatch_cdu_old_actions = cdu_old_actions[start:end]
                minibatch_ct_old_actions = ct_old_actions[start:end]
                minibatch_cdu_old_logprobs = cdu_old_logprobs[start:end]
                minibatch_ct_old_logprobs = ct_old_logprobs[start:end]
                minibatch_cdu_advantages = cdu_advantages[start:end]
                minibatch_ct_advantages = ct_advantages[start:end]
                minibatch_cdu_mc_returns = cdu_mc_returns[start:end]
                minibatch_ct_mc_returns = ct_mc_returns[start:end]


                # Evaluate old actions and values
                cdu_action_logprobs, ct_action_logprobs, cdu_dist_entropy, ct_dist_entropy, state_values = self.policy.evaluate(minibatch_old_states, minibatch_cdu_old_actions, minibatch_ct_old_actions)

                # match state_value tensor dims
                state_values = torch.squeeze(state_values)

                # Find ratio (pi_theta / pi_theta_old)
                cdu_ratios = torch.exp(cdu_action_logprobs - minibatch_cdu_old_logprobs.detach())
                ct_ratios = torch.exp(ct_action_logprobs - minibatch_ct_old_logprobs.detach())

                # Find Surrogate loss, again split into cdu and ct
                cdu_surr1 = cdu_ratios * minibatch_cdu_advantages
                cdu_surr2 = torch.clamp(cdu_ratios, 1-self.eps_clip, 1+self.eps_clip) * minibatch_cdu_advantages
                ct_surr1 = ct_ratios * minibatch_ct_advantages
                ct_surr2 = torch.clamp(ct_ratios, 1-self.eps_clip, 1+self.eps_clip) * minibatch_ct_advantages

                # Loss for CDU & CT
                cdu_loss = -torch.min(cdu_surr1, cdu_surr2) + 0.5 *self.MseLoss(state_values, minibatch_cdu_mc_returns) - 0.01 * cdu_dist_entropy
                ct_loss = -torch.min(ct_surr1, ct_surr2) + 0.5 *self.MseLoss(state_values, minibatch_ct_mc_returns) - 0.01 * ct_dist_entropy
                loss = cdu_loss + ct_loss # simply summing the separate losses, could add hyperparameter for tuning

                # take gradient step
                self.optimizer.zero_grad()
                loss.mean().backward()
                self.optimizer.step()
        
        # Copy new weights into old policy
        self.policy_old.load_state_dict(self.policy.state_dict())

        # clear buffer
        self.buffer_dict['cdu_action'].clear()
        self.buffer_dict['ct_action'].clear()

        return loss.mean().detach().cpu().numpy()
    
    def save(self, checkpoint_path):
        torch.save(self.policy_old.state_dict(), checkpoint_path)
   
    def load(self, checkpoint_path):
        self.policy_old.load_state_dict(torch.load(checkpoint_path, map_location=lambda storage, loc: storage, weights_only=True))
        self.policy.load_state_dict(torch.load(checkpoint_path, map_location=lambda storage, loc: storage, weights_only=True))




