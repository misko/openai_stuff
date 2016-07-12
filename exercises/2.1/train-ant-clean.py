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
small_its=50
#what fraction of results (sorted by score) to keep
keep=0.5
#run this then sample then fit the best 20% and re-do-it
observation = env.reset()
nactions=env.action_space.shape[0]

subspace=nactions/2
#initialize the parameter distribution
layers=[]
layers.append({'in':observation.size+nactions+1,'out':subspace})
layers.append({'in':subspace,'out':subspace})
layers.append({'in':subspace,'out':subspace})
layers.append({'in':subspace,'out':subspace})
layers.append({'in':subspace,'out':nactions})
nparams=0
for d in layers:
	nparams+=d['in']*d['out']
print("network",layers)

meta_param = {'u':np.zeros(nparams),'o':np.ones(nparams)}
for bi in xrange(big_its):
	#sample the parameter distribution
	params = np.random.multivariate_normal(meta_param['u'], np.diag(meta_param['o']), small_its) # add random noise to covar? TODO
	rewards = []
	avg_score=0
	#run for each small iteration
	for i in xrange(small_its):
		param=[]
		param_so_far=0
		for d in layers:
			param.append(params[i][param_so_far:param_so_far+d['in']*d['out']].reshape(d['in'],d['out']))
			param_so_far+=d['in']*d['out']
		reward=[]
		reward_total=0
		old_action = np.zeros(nactions)
		old_observation = np.zeros(observation.size)
		action_diffs=0
		while True:
			l=np.hstack((1,old_action,observation))
			for x in xrange(len(param)):
				l=np.dot(l,param[x])
				if x!=len(param)-1:
					#l=(l * (l>0)) # relu on all but last
					l=np.tanh(l) # sigmoid?
			action=np.clip(l,-1,1)
			action_diffs+=np.abs(action,old_action).sum()
			old_action=action
			old_observation=observation
			observation, reward_f, done, _ = env.step(action)
			reward_total += reward_f
			reward.append(reward_f)
			if done:
			    break
		observation = env.reset()
		avg_score+=reward_total/float(small_its)
		rewards.append((reward_total,i))
		print reward_total,rewards[-1],action_diffs
	rewards.sort()
	#update the parameter distribution
	print "Doing update "
	rewards=rewards[int(len(rewards)*(1-keep)):]
	values=np.zeros((len(rewards),nparams))
	weights=np.zeros(len(rewards))
	j=0
	for x,i in rewards:
		#weights[i]=np.exp(x-rewards[-1][0])
		weights[j]=x-rewards[0][0]
		values[j]=params[i]
		j+=1
	weights=np.clip(weights,0,10)
	weights=weights/weights.sum()	
	average = np.average(values,0, weights=weights)	
	variance = np.average((values-average)**2,0, weights=weights) 
	meta_param['u']=meta_param['u']*0.5+0.5*average
	meta_param['o']=meta_param['o']*0.5+0.5*variance
	print "Doing update - Done "
	print(avg_score)
	print(meta_param['o'].sum())
env.monitor.close()
