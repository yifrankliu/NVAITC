from frontier_env import SmallFrontierModel

# Create and reset the environment
env = SmallFrontierModel()
obs = env.reset()
print(f"Initial observation: {obs}")

# Simple 5-step control loop
for step in range(5):
    action = env.action_space.sample()
    obs, reward, done, info = env.step(action)
    print(
        f"Step {step}: reward={reward}, "
        f"actions={info['actions']}"
    )
    if done:
        break

env.close()