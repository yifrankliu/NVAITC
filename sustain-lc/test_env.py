import pyfmi
from frontier_env import SmallFrontierModel

env = SmallFrontierModel()
obs = env.reset()
print('Observation keys:', obs.keys())
for key, val in obs.items():
    print(f'{key}: {val}')

action = env.action_space.sample()
obs, reward, done, info = env.step(action)
print('Reward:', reward)
print('Done:', done)
