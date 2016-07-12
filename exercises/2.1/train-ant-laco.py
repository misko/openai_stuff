import gym
import numpy as np
import h5py

def save_to_HDF(fname, data):
    """Save data (a dictionary) to a HDF5 file."""
    with h5py.File(fname, 'w') as f:
        for key, item in data.iteritems():
            f[key] = item

def load_from_HDF(fname):
    """Load data from a HDF5 file to a dictionary."""
    data = dict()
    with h5py.File(fname, 'r') as f:
        for key in f:
            data[key] = np.asarray(f[key])
            #print(key + ":", f[key])
    return data

def sampleParams(old_params, layers, big_it, mu, sig, num2sample):
	#l2change = big_it % len(layers)
	rand_mask = np.random.random(size=mu.shape) < 0.33
	new_params = np.random.multivariate_normal(mu, sig, num2sample)
	params = np.tile(mu, (old_params.shape[0], 1))
	params[:,rand_mask] = new_params[:,rand_mask]
	return params, rand_mask

#env = gym.make('CartPole-v0')
#env = gym.make('Acrobot-v0')
#env = gym.make('MountainCar-v0')
env = gym.make('Ant-v1')

env.monitor.start('/tmp/Ant-experiment-2',force=True)

#how many big iteration to do - big iteration is updating the means and variance
big_its=500
#how many small iterations to do for a fixed theta distribution
small_its=30
#what fraction of results (sorted by score) to keep
keep=0.2
#run this then sample then fit the best 20% and re-do-it
observation = env.reset()
nactions=env.action_space.shape[0]

subspace=int(nactions/2)
#initialize the parameter distribution
layers=[]
layers.append({'in':observation.size+nactions+1,'out':subspace})
layers.append({'in':subspace,'out':subspace})
#layers.append({'in':subspace,'out':subspace})
layers.append({'in':subspace,'out':subspace})
layers.append({'in':subspace,'out':nactions})
nparams=0
for d in layers:
	nparams+=d['in']*d['out']
print("network", layers)
print("nparams", nparams)

# parameters initialization
meta_param = {'u':np.zeros(nparams),'o':np.ones(nparams)}
params = np.random.multivariate_normal(meta_param['u'], np.diag(meta_param['o']), small_its)
# train!
try:
	for bi in xrange(big_its):
		#sample the parameter distribution
		params, param_mask = sampleParams(params, layers, bi, meta_param['u'], np.diag(meta_param['o']), small_its)
		#params = np.random.multivariate_normal(meta_param['u'], np.diag(meta_param['o']), small_its) # add random noise to covar? TODO
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
					# if x!=len(param)-1:
					# 	#l=(l * (l>0)) # relu on all but last
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
			action_diffs /= (nactions*len(reward))
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

		mu_new = meta_param['u']*0.5 + 0.5*average
		meta_param['u'][param_mask] = mu_new[param_mask]
		var_new = meta_param['o']*0.5 + 0.5*variance
		meta_param['o'][param_mask] = var_new[param_mask]

		print "Doing update - Done "
		print(avg_score)
		print(meta_param['o'].sum())
except KeyboardInterrupt:
	print("Training terminated")
	pass

env.monitor.close()
# save learned parameters
xp_data = {'params':params, 'mu':meta_param['u'], 'var':meta_param['o'],
			'big_its':big_its, 'small_its':small_its, 'keep':keep}
save_to_HDF('all_param_dump.h5', xp_data)

