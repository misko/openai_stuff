import gym
import numpy as np

#env = gym.make('CartPole-v0')
#env = gym.make('Acrobot-v0')
#env = gym.make('MountainCar-v0')
env = gym.make('Ant-v1')

env.monitor.start('/tmp/Ant-experiment-1',force=True)

#how many big iteration to do - big iteration is updating the means and variance
big_its=500
#how many small iterations to do for a fixed theta distribution
small_its=100
#what fraction of results (sorted by score) to keep
keep=0.2
#run this then sample then fit the best 20% and re-do-it
observation = env.reset()
print(env.action_space)
print(env.action_space.high)
print(env.action_space.low)
nactions=env.action_space.shape[0]
actions=np.zeros(env.action_space.shape) #env.action_space.n 

subspace=nactions/2
#initialize the parameter distribution
#meta_param = {'u':np.random.normal(0, 1, (observation.size*2+2)*actions),'o':np.ones((observation.size*2+2)*actions)}
nparams1=(observation.size*2+1)*subspace
nparams2=(subspace+nactions)*nactions
print  "Using",nparams1,nparams2,"params"
meta_param = {'u':np.zeros(nparams1+nparams2),'o':np.ones(nparams1+nparams2)}
for bi in xrange(big_its):
	#sample the parameter distribution
	params = np.random.multivariate_normal(meta_param['u'], np.diag(meta_param['o']), small_its)
	rewards = []
	avg_score=0
	#run for each small iteration
	for i in xrange(small_its):
		param1=params[i][:nparams1].reshape(nparams1/subspace,subspace)
		param2=params[i][nparams1:].reshape(subspace+nactions,nactions)
		reward_total=0
		old_action = np.zeros(nactions)
		old_observation = np.zeros(observation.size)
		while True:
			#action=np.dot(param[ii*(observation.size*2+2):(ii+1)*(observation.size*2+2)],np.hstack((1,old_action,old_observation,observation)))
			inp=np.hstack((1,old_observation,observation))
			#action=np.clip(np.maximum(0,np.dot(np.dot(inp,param1),param2)),-1,1)
			l1=np.dot(inp,param1)
			l2=np.dot(np.hstack((old_action,(l1 * (l1>0)))),param2) # relu with bias from layer 1?
			action=np.clip(l2,-1,1)
			old_action=action
			old_observation=observation
			observation, reward, done, _ = env.step(np.array([action]))
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
		print bi,i,"SIZE of tops",tops.size
		#print(tops.mean(0))
		meta_param['u']=meta_param['u']*0.5+0.5*tops.mean(0)
		meta_param['o']=meta_param['o']*0.5+0.5*tops.var(0)
	print(avg_score)
	#print(meta_param)
env.monitor.close()
