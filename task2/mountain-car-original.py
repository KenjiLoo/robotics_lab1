import gym
import numpy as np
import matplotlib.pyplot as plt

MAX_NUM_EPISODES = 10000
STEPS_PER_EPISODE = 200  #This is specific to MountainCar. May change with env
EPSILON_MIN = 0.005
max_num_steps = MAX_NUM_EPISODES * STEPS_PER_EPISODE
EPSILON_DECAY = 500 * EPSILON_MIN / max_num_steps
ALPHA = 0.01  # Learning rate
GAMMA = 0.98  # Discount factor
NUM_DISCRETE_BINS = 30  # Number of bins to Discretize each observation dim
rewards = []

class Q_Learner(object):
    def __init__(self, env):
        self.obs_shape = env.observation_space.shape
        self.obs_high = env.observation_space.high
        self.obs_low = env.observation_space.low
        self.obs_bins = NUM_DISCRETE_BINS  # Number of bins to Discretize each observation dim
        self.bin_width = (self.obs_high - self.obs_low) / self.obs_bins
        self.action_shape = env.action_space.n
        # Create a multi-dimensional array (aka. Table) to represent the
        # Q-values
        self.Q = np.zeros((self.obs_bins + 1, self.obs_bins + 1,
                           self.action_shape))  # (51 x 51 x 3)
        self.alpha = ALPHA  # Learning rate
        self.gamma = GAMMA  # Discount factor
        self.epsilon = 1.0

    def discretize(self, obs):
        return tuple(((obs - self.obs_low) / self.bin_width).astype(int))

    def get_action(self, obs):
        discretized_obs = self.discretize(obs)
        return np.argmax(self.Q[discretized_obs])

    def learn(self, obs, action, reward, next_obs):
        discretized_obs = self.discretize(obs)
        discretized_next_obs = self.discretize(next_obs)
        td_target = reward + self.gamma * np.max(self.Q[discretized_next_obs])
        td_error = td_target - self.Q[discretized_obs][action]
        self.Q[discretized_obs][action] += self.alpha * td_error

def train(agent, env):
    best_reward = -float('inf')

    rewards_streak = 0
    for episode in range(MAX_NUM_EPISODES):
        done = False
        obs, _ = env.reset()
        total_reward = 0.0
        while not done:
            action = agent.get_action(obs)
            next_obs, reward, done, info, _ = env.step(action)
            agent.learn(obs, action, reward, next_obs)
            obs = next_obs
            total_reward += reward
        if total_reward > best_reward:
            best_reward = total_reward
        print("Episode#:{} reward:{} best_reward:{}".format(episode,
                                     total_reward, best_reward))

        # reward streak conditions
        rewards.append(total_reward)
        prev_ep = episode-1
        if (episode!=0) and ((rewards[episode]//10) == (rewards[prev_ep]//10)):
            rewards_streak += 1
            print("Episode:{}, Streak:{}".format(episode, rewards_streak))
            if (rewards_streak == 1000): #change values here to set the amount of episodes to get same reward
                print("Solved, with reward streak:{}".format(rewards_streak))
                print("Best Reward: {}".format(best_reward))
                break
        elif ((rewards[episode]//10) != (rewards[prev_ep]//10)):
            rewards_streak = 0

        # update learning rate conditions
        if (episode == (MAX_NUM_EPISODES/2)):
            ALPHA = 0.05

    # Return the trained policy
    return np.argmax(agent.Q, axis=2)


def test(agent, env, policy):
    done = False
    obs, _ = env.reset()
    total_reward = 0.0
    while not done:
        action = policy[agent.discretize(obs)]
        next_obs, reward, done, info, _ = env.step(action)
        # print(info)
        obs = next_obs
        total_reward += reward
        # print("Reward in iteration:{}:".format( total_reward ))
    return total_reward


if __name__ == "__main__":
    env = gym.make('MountainCar-v0')
    agent = Q_Learner(env)
    learned_policy = train(agent, env)
    # Use the Gym Monitor wrapper to evalaute the agent and record video
    # gym_monitor_path = "./gym_monitor_output"
    # env = gym.wrappers.Monitor(env, gym_monitor_path, force=True)

    env.close()

    plt.figure("mountaincar original")
    plt.plot(range(MAX_NUM_EPISODES), rewards)
    plt.xlabel('Number of Episodes')
    plt.ylabel('Rewards')
    plt.show()

# test is problematic
#     for _ in range(1000):
#         test_reward = test(agent, env, learned_policy)
#         print("Test Iteration:{}, Test Reward:{}".format(_, test_reward ))