import gym
import numpy as np

#env = gym.make('CartPole-v0')
env = gym.make('Acrobot-v0')

env.monitor.start('/tmp/cartpole-experiment-1',force=True)

#how many big iteration to do - big iteration is updating the means and variance
big_its=200
#how many small iterations to do for a fixed theta distribution
small_its=100
#what fraction of results (sorted by score) to keep
keep=0.2

#run this then sample then fit the best 20% and re-do-it
observation = env.reset()
#initialize the parameter distribution
meta_param = {'u':np.random.normal(0, 1, observation.size),'o':np.diag(np.ones(observation.size))}
for bi in xrange(big_its):
	#sample the parameter distribution
	params = np.random.multivariate_normal(meta_param['u'], meta_param['o'], small_its)
	rewards = []
	avg_score=0
	#run for each small iteration
	for i in xrange(small_its):
		param=params[i]
		reward_total=0
		while True:
			action = 1 if np.dot(param, observation) > 0 else 0
			observation, reward, done, _ = env.step(action)
			reward_total += reward
			if done:
			    break
		observation = env.reset()
		avg_score+=reward_total/float(small_its)
		rewards.append((reward_total,i))
	rewards.sort()
	#update the parameter distribution
	tops=np.vstack([ params[i] for x,i in rewards[int(len(rewards)*(1-keep)):] ])
	meta_param['u']=meta_param['u']*0.5+0.5*tops.mean(0)
	meta_param['o']=meta_param['o']*0.5+0.5*np.cov(tops,rowvar=0)
	print(avg_score)
	print(meta_param)
env.monitor.close()
