import gym
import numpy as np

#env = gym.make('CartPole-v0')
#env = gym.make('Acrobot-v0')
env = gym.make('MountainCar-v0')
#env = gym.make('InvertedPendulum-v1')

env.monitor.start('/tmp/cartpole-experiment-1',force=True)

#how many big iteration to do - big iteration is updating the means and variance
big_its=200
#how many small iterations to do for a fixed theta distribution
small_its=100
#what fraction of results (sorted by score) to keep
keep=0.2
#run this then sample then fit the best 20% and re-do-it
observation = env.reset()
#print(env.action_space)
#print(env.action_space.high)
#print(env.action_space.low)
actions=env.action_space.n 
#initialize the parameter distribution
#meta_param = {'u':np.random.normal(0, 1, (observation.size*2+2)*actions),'o':np.ones((observation.size*2+2)*actions)}
meta_param = {'u':np.zeros((observation.size*2+2)*actions),'o':np.ones((observation.size*2+2)*actions)}
for bi in xrange(big_its):
	#sample the parameter distribution
	params = np.random.multivariate_normal(meta_param['u'], np.diag(meta_param['o']), small_its)
	rewards = []
	avg_score=0
	#run for each small iteration
	for i in xrange(small_its):
		param=params[i]
		reward_total=0
		old_action = 0
		old_observation = np.zeros(observation.size)
		while True:
			action_acts = []
			for ii in xrange(actions):
				action_acts.append((np.dot(param[ii*(observation.size*2+2):(ii+1)*(observation.size*2+2)],np.hstack((1,old_action,old_observation,observation))),ii))
			action_acts.sort()
			action=action_acts[-1][1]
			old_action=action
			old_observation=observation
			observation, reward, done, _ = env.step(action)
			reward_total += reward
			if done:
			    break
		observation = env.reset()
		avg_score+=reward_total/float(small_its)
		rewards.append((reward_total,i))
	rewards.sort()
	#update the parameter distribution
	if rewards[0][0]==rewards[-1][0]:
		print "uhhh ohhh"
		#small_its=int(1.5*small_its)
		#meta_param = {'u':np.random.normal(0, 1, (observation.size*2+2)*actions),'o':np.ones((observation.size*2+2)*actions)}
		#elif rewards[0][0]==rewards[int(len(rewards)*(1-keep/2))][0]:
		meta_param['o']=meta_param['o']*1.1
	elif rewards[0][0]==rewards[-2][0]:
		#small_its=int(small_its*1.5)
		#meta_param = {'u':np.random.normal(0, 1, (observation.size*2+2)*actions),'o':np.ones((observation.size*2+2)*actions)}
		print "TOO SMALL SMAPLING"
		meta_param['o']=meta_param['o']*1.1
	else:
		tops=np.vstack([ params[i] for x,i in rewards[int(len(rewards)*(1-keep)):] if x!=rewards[0][0]])
		print "SIZE of tops",tops.size
		print(tops.mean(0))
		meta_param['u']=meta_param['u']*0.5+0.5*tops.mean(0)
		meta_param['o']=meta_param['o']*0.5+0.5*tops.var(0)
	print(avg_score)
	print(meta_param)
env.monitor.close()
