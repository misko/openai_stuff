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
layers=[]
#layers.append({'in':observation.size*2+nactions+1,'out':subspace})
layers.append({'in':observation.size+nactions+1,'out':subspace})
layers.append({'in':subspace,'out':subspace})
#layers.append({'in':subspace,'out':subspace})
layers.append({'in':subspace,'out':subspace})
layers.append({'in':subspace,'out':nactions})
nparams=0
for d in layers:
	nparams+=d['in']*d['out']
print("network",layers)

#random on no diags
covar = np.random.rand(nparams,nparams)-0.5
covar = np.dot(covar,covar.transpose())
covar = covar/covar.max()
np.fill_diagonal(covar,0)
#print(covar)
#binary on non diags


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
			#action=np.dot(param[ii*(observation.size*2+2):(ii+1)*(observation.size*2+2)],np.hstack((1,old_action,old_observation,observation)))
			#l=np.hstack((1,old_action,old_observation,observation))
			l=np.hstack((1,old_action,observation))
			for x in xrange(len(param)):
				l=np.dot(l,param[x])
				if x!=len(param)-1:
					l=(l * (l>0)) # relu on all but last
			#action=np.clip(np.maximum(0,np.dot(np.dot(inp,param1),param2)),-1,1)
			#l1=np.dot(inp,param1)
			#l2=np.dot((l1 * (l1>0)),param2) # relu with bias from layer 1?
			#l3=np.dot((l2 * (l2>0)),param3)
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
		#rewards.append((reward_total,i))
		#rewards.append((reward_total/(1+np.var(reward)),i))

		#more variance, doesnt stall the system?
		#rewards.append((reward_total*(1+5*np.var(reward)),i)) 

		action_diffs/=(nactions*len(reward))

		#rewards at the end are better!!
		rt=0
		for x in xrange(len(reward)):
			rt+=reward[x]*(0.5+float(x)/len(reward))
		#rewards.append((rt,i))
		#rewards.append((rt*(1+5*np.var(reward)),i)) 
		#rewards.append((rt*(1+5*np.var(reward))-reward_total,i)) 
		#rewards.append((rt*(1+5*np.var(reward)*(0.5+action_diffs/2))-reward_total,i)) 
		rewards.append((rt*(1+5*action_diffs)-reward_total,i)) 
		print reward_total,rewards[-1]
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
		print "Doing update "
		softmax=True
		if softmax: 
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
			#meta_param['o']=np.clip(meta_param['o']*0.1+0.9*variance,0.1,10)
			meta_param['o']=meta_param['o']*0.5+0.5*variance
		else:
			tops=np.vstack([ params[i] for x,i in rewards[int(len(rewards)*(1-keep)):] if x!=rewards[0][0]])
			print bi,i,"SIZE of tops",tops.size
			#print(tops.mean(0))
			meta_param['u']=meta_param['u']*0.5+0.5*tops.mean(0)
			meta_param['o']=np.clip(meta_param['o']*0.5+0.5*tops.var(0),0.1,10)
		print "Doing update - Done "
	print(avg_score)
	print(meta_param['o'].sum())
env.monitor.close()
