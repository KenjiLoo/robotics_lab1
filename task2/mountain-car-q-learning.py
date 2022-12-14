#--------------------------------------------------------#
import gym
import numpy as np
import matplotlib.pyplot as plt
import math
import time
from numpy import random
#--------------------------------------------------------#
MAX_NUM_EPISODES = 10000
STEPS_PER_EPISODE = 200  # This is specific to MountainCar. May change with env
EPSILON_MIN = 0.005
max_num_steps = MAX_NUM_EPISODES * STEPS_PER_EPISODE
EPSILON_DECAY = 500 * EPSILON_MIN / max_num_steps
ALPHA = 0.01  # Learning rate
GAMMA = 0.98  # Discount factor
NUM_DISCRETE_BINS = 30  # Number of bins to Discretize each observation dim
rewards = [] # Collects rewards info
#--------------------------------------------------------#

"""
(Class) 'Q_Learner' defines the essential functions needed to training. 
@param object -> takes in the environment
"""
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

    """
    (Method) 'discretize' returns the environment in discretized values
    @param self -> access class attributes
    @param obs -> observation space of the environment
    """
    def discretize(self, obs):
        return tuple(((obs - self.obs_low) / self.bin_width).astype(int))

    """
    (Method) 'get_action' defines the epsilon-greedy policy
    @param self -> access class attributes
    @param obs -> observation space of the environment
    """
    def get_action(self, obs):
        # print("breaks here")
        discretized_obs = self.discretize(obs)
        if np.random.random() > self.epsilon:
            return np.argmax(self.Q[discretized_obs])
        else:  # Choose a random action
            return np.random.choice([a for a in range(self.action_shape)])

    """
    (Method) 'learn' defines the rules used in training
    @param self -> access class attributes
    @param obs -> observation space of the environment
    @param action -> state action value
    @param reward -> reward from current episode
    @param next_obs -> next observation space state
    """
    def learn(self, obs, action, reward, next_obs):
        discretized_obs = self.discretize(obs)
        discretized_next_obs = self.discretize(next_obs)
        td_target = reward + self.gamma * np.max(self.Q[discretized_next_obs])
        td_error = td_target - self.Q[discretized_obs][action]
        self.Q[discretized_obs][action] += self.alpha * td_error

#--------------------------------------------------------#

"""
(Function) 'train' executes the training of the agent
@param agent -> takes in the information of the agent
@param env -> defines the environment
"""
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

        # Reward streak conditions
        # Terminates train() if streak conditions are met
        rewards.append(total_reward)
        prev_ep = episode-1

        # If reward of current episode's floor division
        # is equal to the previous episode,
        # reward streak + 1
        if (episode!=0) and ((rewards[episode]//10) == (rewards[prev_ep]//10)):
            rewards_streak += 1
            print("Episode:{}, Streak:{}".format(episode, rewards_streak))
            # Achieve streak for 1000 times to terminate train()
            if (rewards_streak == 1000):
                print("Solved, with reward streak:{}".format(rewards_streak))
                print("Best Reward: {}".format(best_reward))
                break
        # Reset streak count if streak breaks
        elif ((rewards[episode]//10) != (rewards[prev_ep]//10)):
            rewards_streak = 0

        # Update learning rate conditions
        if (episode == (MAX_NUM_EPISODES/2)):
            ALPHA = 0.05

    # Return the trained policy
    return np.argmax(agent.Q, axis=2)

#--------------------------------------------------------#

if __name__ == "__main__":
    env = gym.make('MountainCar-v0')
    agent = Q_Learner(env)
    learned_policy = train(agent, env)
    env.close()

    # Plotting the results, rewards per episode during training
    # x-axis - Number of episodes
    # y-axis - Rewards
    plt.figure("mountaincar updated")
    plt.plot(range(MAX_NUM_EPISODES), rewards)
    plt.xlabel('Number of Episodes')
    plt.ylabel('Rewards')
    plt.show()

#--------------------------------------------------------#
