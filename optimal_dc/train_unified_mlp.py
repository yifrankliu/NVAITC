import os
from datetime import datetime
import torch
import numpy as np
from torch.utils.tensorboard import SummaryWriter

# --- make the sustain-lc submodule importable (repo-relative, move-safe) ---
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "external" / "sustain-lc"))
# ---------------------------------------------------------------------------
from unified_mlp_baseline import Unified_PPO
from frontier_env import SmallFrontierModel

def flatten_state(state_dict):
    """
    This function is modified, instead of batchifying for each component, it groups all
    component observations into one array to be acted on by one unified agent.
    """
    flattened = np.concatenate([state_dict['cdu-cabinet-1'],
                    state_dict['cdu-cabinet-2'],
                    state_dict['cdu-cabinet-3'],
                    state_dict['cdu-cabinet-4'],
                    state_dict['cdu-cabinet-5'],
                    state_dict['cooling-tower-1']])
    
    return flattened

def categorize_actions(actions):
    
    actions_categories_dict = {'CDUCAB': ['cdu-cabinet-1', 'cdu-cabinet-2', 'cdu-cabinet-3', 'cdu-cabinet-4', 'cdu-cabinet-5'],
                                          'CT': ['cooling-tower-1']}
    categorized_actions = {}
    for agent_id, action in actions.items():
        if agent_id == 'CDUCAB':
            for i, action_category in enumerate(actions_categories_dict[agent_id]):
                categorized_actions[action_category] = action[i]
        else:
            categorized_actions[actions_categories_dict[agent_id][0]] = action
            
    return categorized_actions

# pylint: disable=C0303,C0301,C0116,C0103,C0209,W1514,W0311
################################### Training ###################################
def train():
    print("============================================================================================")

    ####### initialize environment hyperparameters ######
    env_name = "SmallFrontierModel"  # environment name

    max_ep_len = 200                   # max timesteps in one episode
    max_training_timesteps = int(3e6)   # break training loop if timeteps > max_training_timesteps

    print_freq = max_ep_len * 10        # print avg reward in the interval (in num timesteps)
    log_freq = max_ep_len * 5           # log avg reward in the interval (in num timesteps)
    save_model_freq = int(2e3)          # save model frequency (in num timesteps)
    best_reward = float('-inf')  # initialize best reward as negative infinity
    print_avg_reward = 0                # initialize average reward

    action_std = 0.6                    # starting std for action distribution (Multivariate Normal)
    action_std_decay_rate = 0.05        # linearly decay action_std (action_std = action_std - action_std_decay_rate)
    min_action_std = 0.1                # minimum action_std (stop decay after action_std <= min_action_std)
    action_std_decay_freq = int(2.5e5)  # action_std decay frequency (in num timesteps)
    #####################################################

    ## Note : print/log frequencies should be > than max_ep_len

    ################ PPO hyperparameters ################
    update_timestep = max_ep_len * 1      # update policy every n timesteps
    K_epochs = 50               # update policy for K epochs in one PPO update

    eps_clip = 0.2          # clip parameter for PPO
    gamma = 0.80            # discount factor

    lr_cdu_actor = 0.0003
    lr_ct_actor = 0.0003       # learning rate for actor network
    lr_critic = 0.001       # learning rate for critic network

    random_seed = 123         # set random seed if required (0 = no random seed)
    #####################################################

    print("training environment name : " + env_name)
    run_num_pretrained = 3    #### change this to prevent overwriting weights in same env_name folder
    reward_fn_version = 2
    exogen_gen_v = 2
    env = SmallFrontierModel(use_reward_shaping = f'reward_shaping_v{reward_fn_version}', exogen_gen_v = exogen_gen_v)
    print("Using Reward Shaping Version : ", env.use_reward_shaping)

    ###################### logging ######################

    #### log files for multiple runs are NOT overwritten
    log_dir = "Unified_MLP_logs"
    if not os.path.exists(log_dir):
          os.makedirs(log_dir)

    log_dir = log_dir + '/' + env_name
    if not os.path.exists(log_dir):
          os.makedirs(log_dir)

    #### get number of log files in log directory
    run_num = 0
    current_num_files = next(os.walk(log_dir))[2]
    run_num = len(current_num_files)

    #### create new log file for each run
    log_f_name = log_dir + '/Unified_MLP_' + env_name + "_log_" + str(run_num) + ".csv"

    print("current logging run number for " + env_name + " : ", run_num)
    print("logging at : " + log_f_name)
    #####################################################

    ################### checkpointing ###################
    directory = "Unified_MLP_preTrained"
    if not os.path.exists(directory):
          os.makedirs(directory)

    directory = directory + '/' + env_name + '/'
    if not os.path.exists(directory):
          os.makedirs(directory)

    # create one single checkpoint
    checkpoint_path = directory + "PPO_{}_{}_{}_unified.pth".format(env_name, random_seed, run_num_pretrained)
    #####################################################


    ############# print all hyperparameters #############
    print("--------------------------------------------------------------------------------------------")
    print("Unified single-agent MLP (CDU continuous + CT discrete)")
    print("max training timesteps : ", max_training_timesteps)
    print("max timesteps per episode : ", max_ep_len)
    print("model saving frequency : " + str(save_model_freq) + " timesteps")
    print("log frequency : " + str(log_freq) + " timesteps")
    print("printing average reward over episodes in last : " + str(print_freq) + " timesteps")
    print("--------------------------------------------------------------------------------------------")
    print("state space dimension : ", 34)
    print("CDU action space dimension : ", 25)
    print("CT action space dimension : ", 9)
    print("--------------------------------------------------------------------------------------------")
    print("starting std of CDU action distribution : ", action_std)
    print("decay rate of std of action distribution : ", action_std_decay_rate)
    print("minimum std of action distribution : ", min_action_std)
    print("decay frequency of std of action distribution : " + str(action_std_decay_freq) + " timesteps")
    print("--------------------------------------------------------------------------------------------")
    print("PPO update frequency : " + str(update_timestep) + " timesteps")
    print("PPO K epochs : ", K_epochs)
    print("PPO epsilon clip : ", eps_clip)
    print("discount factor (gamma) : ", gamma)
    print("--------------------------------------------------------------------------------------------")
    print("optimizer learning rate CDU actor : ", lr_cdu_actor)
    print("optimizer learning rate CT actor : ", lr_ct_actor)
    print("optimizer learning rate critic : ", lr_critic)
    if random_seed:
        print("--------------------------------------------------------------------------------------------")
        print("setting random seed to ", random_seed)
    torch.manual_seed(random_seed)
    env.seed(random_seed)  # pylint: disable=no-member
    np.random.seed(random_seed)
    #####################################################

    print("============================================================================================")

    ################# training procedure ################

    # initialize a PPO agent
    ppo_agent = Unified_PPO(state_dim=34, cdu_action_dim=25, ct_action_dim=9, num_centralized_actions=1,
                            lr_cdu_actor=lr_cdu_actor, lr_ct_actor=lr_ct_actor, lr_critic=lr_critic,
                            gamma=gamma, K_epochs=K_epochs, eps_clip=eps_clip,
                            cdu_action_std_init=action_std)

    # track total training time
    start_time = datetime.now().replace(microsecond=0)
    print("Started training at (GMT) : ", start_time)

    print("============================================================================================")
    
    ################# tensorboard logging ################
    writer = SummaryWriter()
    
    print("============================================================================================")

    # logging file
    log_f = open(log_f_name,"w+")
    log_f.write('episode,timestep,reward_CDUCAB, reward_CT\n')

    # printing and logging variables
    print_running_reward = {'CDUCAB' : 0, 'CT' : 0}
    print_running_episodes = 0
    print_avg_reward = {'CDUCAB' : 0, 'CT' : 0}

    log_running_reward = {'CDUCAB' : 0, 'CT' : 0}
    log_running_episodes = 0
    log_avg_reward = {'CDUCAB' : 0, 'CT' : 0}
    
    time_step = 0
    i_episode = 0

    # training loop
    while time_step <= max_training_timesteps:

        state = env.reset()
        flattened = flatten_state(state)
        current_ep_reward = {'CDUCAB' : 0, 'CT' : 0}
        # create custom tb logging for cabinet episode reward
        cabinet_totalepisode_reward = {'cdu-cabinet-1':0, 'cdu-cabinet-2':0, 'cdu-cabinet-3':0, 'cdu-cabinet-4':0, 'cdu-cabinet-5':0}

        for _ in range(1, max_ep_len+1):

            actions = {}  # list to store actions for each agent

            # modified: one call for both cdu & ct actions
            cdu_action, ct_action = ppo_agent.select_action(flattened)
            actions['CDUCAB'] = cdu_action
            actions['CT'] = ct_action
            
            # categorize actions in to dict format for env
            categorized_actions = categorize_actions(actions)

            state, rewards, done, _ = env.step(categorized_actions)
            flattened = flatten_state(state)
            
            # collect next state for bootstrap value calculation
            ppo_agent.next_state = flattened

            # manually append rewards and terminals to each buffer
            reward = {
                    'CDUCAB' : (rewards['cdu-cabinet-1']+
                                rewards['cdu-cabinet-2']+
                                rewards['cdu-cabinet-3']+
                                rewards['cdu-cabinet-4']+
                                rewards['cdu-cabinet-5'])/5.0,
                        'CT' : rewards['cooling-tower-1']
                    }
            ppo_agent.buffer_dict['cdu_action'].rewards.append(reward['CDUCAB'])
            ppo_agent.buffer_dict['cdu_action'].is_terminals.append(done['cdu-cabinet-1'])
            ppo_agent.buffer_dict['ct_action'].rewards.append(reward['CT'])
            ppo_agent.buffer_dict['ct_action'].is_terminals.append(done['cooling-tower-1'])
            current_ep_reward['CDUCAB'] += reward['CDUCAB']
            current_ep_reward['CT'] += reward['CT']
            
            for k,v in rewards.items():
                if k!= 'cooling-tower-1':
                    cabinet_totalepisode_reward[k] += v
                
            time_step += 1

            # update PPO agent for each agent
            if time_step % update_timestep == 0:

                ppo_loss = ppo_agent.update()
                writer.add_scalar('Loss', ppo_loss, time_step)

            if time_step % action_std_decay_freq == 0:
                ppo_agent.decay_action_std(action_std_decay_rate, min_action_std)
    

            # log in logging file
            if time_step % log_freq == 0:

                # log average reward till last episode for each agent
                log_avg_reward['CDUCAB'] = log_running_reward['CDUCAB'] / log_running_episodes
                log_avg_reward['CDUCAB'] = round(log_avg_reward['CDUCAB'], 4)
                
                log_avg_reward['CT'] = log_running_reward['CT'] / log_running_episodes
                log_avg_reward['CT'] = round(log_avg_reward['CT'], 4)

                log_f.write('Episode No. : {}, timestep : {}, CDUCAB : {}, CT : {}\n'.format(i_episode, time_step, 
                                                                                             log_avg_reward['CDUCAB'], log_avg_reward['CT']))
                log_f.flush()

                log_running_reward = {'CDUCAB' : 0, 'CT' : 0}
                log_running_episodes = 0

            # printing average reward
            if time_step % print_freq == 0:

                print_avg_reward['CDUCAB'] = print_running_reward['CDUCAB'] / print_running_episodes
                print_avg_reward['CDUCAB'] = round(print_avg_reward['CDUCAB'], 2)
                
                print_avg_reward['CT'] = print_running_reward['CT'] / print_running_episodes
                print_avg_reward['CT'] = round(print_avg_reward['CT'], 2)

                print("Episode : {} \t\t Timestep : {} \t\t Average Reward CDUCAB : {} \t\t Average Reward CT: {}".format(i_episode, time_step,
                                                                                                print_avg_reward['CDUCAB'], print_avg_reward['CT'] ))

                print_running_reward = {'CDUCAB' : 0, 'CT' : 0}
                print_running_episodes = 0

            # save loop removed, replaced with just one agent save
            if (time_step % save_model_freq  == 0):
                if (print_avg_reward['CDUCAB'] > best_reward):
                        best_reward = print_avg_reward['CDUCAB']
                        print("--------------------------------------------------------------------------------------------")
                        print("saving model at : " + checkpoint_path)
                        ppo_agent.save(checkpoint_path)
                        print("model saved")

                print("Elapsed Time  : ", datetime.now().replace(microsecond=0) - start_time)
                print("--------------------------------------------------------------------------------------------")
                
                    

            # collect energy and temperature data from info dictionary
            # energy_trace.append(info['coo.Q_flow'])
            # server1_temp_trace.append(info['serverblock1.heatCapacitor.T'])
            
            # break; if the episode is over
            # if done:
            #     break
            
        
        # Log variables from the info dictionary to TensorBoard
        writer.add_scalar('Episode Reward CDUCAB', current_ep_reward['CDUCAB'], i_episode)
        writer.add_scalar('Episode Reward CT', current_ep_reward['CT'], i_episode) 
        
        # log per cabinet reward
        for k,v in cabinet_totalepisode_reward.items():
            writer.add_scalar(f'Episode Reward {k}', v, i_episode)  
        
        # writer.add_scalar('Energy/CumulativeOneEpisode(kWh)', sum(energy_trace)/1000, i_episode)
        # writer.add_scalar('Server1_Temperature/mean', np.mean(server1_temp_trace) - 273.15, i_episode)
        
        print_running_reward['CDUCAB'] += current_ep_reward['CDUCAB']
        print_running_reward['CT'] += current_ep_reward['CT']
        print_running_episodes += 1

        log_running_reward['CDUCAB'] += current_ep_reward['CDUCAB']
        log_running_reward['CT'] += current_ep_reward['CT']
        log_running_episodes += 1

        i_episode += 1

    log_f.close()
    env.close()

    # print total training time
    print("============================================================================================")
    end_time = datetime.now().replace(microsecond=0)
    print("Started training at: ", start_time)
    print("Finished training at: ", end_time)
    print("Total training time  : ", end_time - start_time)
    print("============================================================================================")


if __name__ == '__main__':

    train()