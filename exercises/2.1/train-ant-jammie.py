import gym
import numpy as np

env = gym.make('Ant-v1')
env.monitor.start('/tmp/Ant-experiment-1',force=True)

#how many big iteration to do - big iteration is updating the means and variance
big_its=500
#how many small iterations to do for a fixed theta distribution
small_its=100
#what fracion of results (sorted by score) to keep
keep=int(small_its*0.2)

#run this then sample then fit the best 20% and re-do-it
observation = env.reset()
nactions=env.action_space.shape[0]
subspace=nactions*4


def avg_from_list(l):
	n=np.zeros(len(l))
	idx=0
	for x,i in l:
		n[idx]=x
		idx+=1
	return np.average(n),np.var(n)

#initialize the parameter distribution
layers=[]
layers.append({'in':observation.size+1,'out':subspace})
layers.append({'in':subspace+1,'out':subspace})
layers.append({'in':subspace+1,'out':subspace})
layers.append({'in':subspace+1,'out':nactions})

#initialize the network
fancy_init=True
for d in layers:
	d['u']=np.zeros(d['in']*d['out'])
	if fancy_init:
		#d['o']=np.ones(d['in']*d['out'])*4.0/(d['in']+d['out']) # for ReLU? #Kaiming He  "Delving Deep into Rectifiers: Surpassing Human-Level Performance on ImageNet Classification"
		d['o']=np.ones(d['in']*d['out'])*2.0/(d['in']+d['out']) # for sigmoid #Xavier Glorot & Yoshua Bengios Understanding the difficulty of training deep feedforward neural networks.
	else:
		d['o']=np.ones(d['in']*d['out'])

rewards = []
for bi in xrange(big_its):
	#sample the parameters for ech layer
	for d in layers:
		d['params'] = np.random.multivariate_normal(d['u'], np.diag(d['o']), small_its).reshape(small_its,d['in'],d['out']) 
		d['acts'] = []
	#run for each small iteration
	for i in xrange(small_its):
		reward=[]
		reward_total=0
		while True:
			l=observation
			for d in layers:
				l=np.dot(np.hstack((l,1)),d['params'][i])
				#l=(l * (l>0)) # ReLU
				l=np.tanh(l) # sigmoid
				d['acts'].append(l>0)
			action=np.clip(l,-1,1) # clip the output values to make sure its in the range
			observation, reward_f, done, _ = env.step(action) # do a step in openAI
			reward.append(reward_f) # keep track of the reward for each step
			if done: # if the simulation is done - out of bounds, or out of time
			    observation = env.reset() # reset to a new training episode
			    break # while true doesnt break easy...
		rewards.append((sum(reward),i)) # put the score and which example it was into a list
	#sort the list by the score, so that the best ones are at the end
	rewards.sort()
	#Only keep the 'elite' fraction
	#update each layers distribution
	rewards_non_elite=rewards[:-keep]
	rewards_elite=rewards[-keep:]
	avg,var=avg_from_list(rewards)
	avg_non_elite,var_non_elite=avg_from_list(rewards_non_elite)
	avg_elite,var_elite=avg_from_list(rewards_elite)

	vs=[]
	ms=[]
	for d in layers:
		values=np.zeros((len(rewards_elite),d['in'],d['out']))
		j=0
		for x,i in rewards_elite:
			values[j]=d['params'][i]
			j+=1
		average = np.average(values,0)
		variance = np.average((values-average)**2,0)
		d['u']=d['u']*0.5+0.5*average.flatten()
		d['o']=d['o']*0.5+0.5*variance.flatten()
		vs.append("%0.2f" % d['o'].sum())
		ms.append("%0.2f" % d['u'].mean())
	rewards = []
	print("Neuron Acts",np.average(d['acts'],0))
	print "Doing update - Avg(all,non-elite,elite)",avg,avg_non_elite,avg_elite,"Vars",vs,"Means",ms
env.monitor.close()
