import gym
import numpy as np

env = gym.make('Ant-v1')
env.monitor.start('/tmp/Ant-experiment-1',force=True)

#how many big iteration to do - big iteration is updating the means and variance
big_its=500
#how many small iterations to do for a fixed theta distribution
small_its=30
#what fracion of results (sorted by score) to keep
keep=0.5

#run this then sample then fit the best 20% and re-do-it
observation = env.reset()
nactions=env.action_space.shape[0]
subspace=nactions/2

#initialize the parameter distribution
layers=[]
layers.append({'in':observation.size,'out':subspace})
layers.append({'in':subspace,'out':subspace})
layers.append({'in':subspace,'out':subspace})
layers.append({'in':subspace,'out':nactions})

#initialize the network
fancy_init=True
for d in layers:
	d['u']=np.zeros(d['in']*d['out'])
	if fancy_init:
		#d['o']=np.ones(d['in']*d['out'])*4.0/(d['in']+d['out']) # for ReLU? #Kaiming He  "Delving Deep into Rectifiers: Surpassing Human-Level Performance on ImageNet Classification"
		d['o']=np.ones(d['in']*d['out'])*2.0/(d['in']+d['out']) # for sigmoid #Xavier Glorot & Yoshua Bengios Understanding the difficulty of training deep feedforward neural networks.
	else:
		d['o']=np.ones(d['in']*d['out'])

for bi in xrange(big_its):
	#sample the parameters for ech layer
	for d in layers:
		d['params'] = np.random.multivariate_normal(d['u'], np.diag(d['o']), small_its).reshape(small_its,d['in'],d['out']) 
		d['acts'] = []
		#d['params'] = np.random.uniform(low=-1,high=1,size=d['in']*d['out']*small_its).reshape(small_its,d['in']*d['out'])
		#d['params'] = (d['params']*np.tile(d['o'],(small_its,1))+np.tile(d['u'],(small_its,1))).reshape(small_its,d['in'],d['out'])
	rewards = []
	avg_score=0
	#run for each small iteration
	for i in xrange(small_its):
		reward=[]
		reward_total=0
		while True:
			l=observation
			for d in layers:
				l=np.dot(l,d['params'][i])
				#l=(l * (l>0)) # ReLU
				l=np.tanh(l) # sigmoid
				d['acts'].append(l>0)
			action=np.clip(l,-1,1) # clip the output values to make sure its in the range
			observation, reward_f, done, _ = env.step(action) # do a step in openAI
			reward.append(reward_f) # keep track of the reward for each step
			if done: # if the simulation is done - out of bounds, or out of time
			    observation = env.reset() # reset to a new training episode
			    break # while true doesnt break easy...
		avg_score+=sum(reward)/float(small_its) # the average score per episode
		rewards.append((sum(reward),i)) # put the score and which example it was into a list
	#sort the list by the score, so that the best ones are at the end
	rewards.sort()
	#Only keep the 'elite' fraction
	rewards=rewards[int(len(rewards)*(1-keep)):]
	#update each layers distribution
	var_sum=[]
	fancy_update=True
	if fancy_update:
		weights=np.zeros(len(rewards))
		j=0
		for x,i in rewards:
			weights[j]=x-rewards[0][0]
			j+=1
		weights=np.clip(weights,0,10)
		weights=weights/weights.sum()	
		for d in layers:
			#checkout the activations	
			d['acts']=np.vstack(d['acts'])*1 # bool -> int
			print(np.average(d['acts'],0))
			values=np.zeros((len(rewards),d['in'],d['out']))
			j=0
			for x,i in rewards:
				values[j]=d['params'][i]
				j+=1
			average = np.average(values,0, weights=weights)
			variance = np.average((values-average)**2,0, weights=weights)
			#average = np.average(d['params'],0).flatten()
			#variance = np.var(d['params'],0).flatten()
			average=average.flatten()
			variance=variance.flatten() 
			d['u']=d['u']*0.5+0.5*average
			d['o']=d['o']*0.5+0.5*variance
			var_sum.append(d['o'].sum())
	else:
		for d in layers:
			average = np.average(d['params'],0).flatten()
			variance = np.var(d['params'],0).flatten()
			d['u']=d['u']*0.5+0.5*average
			d['o']=d['o']*0.5+0.5*variance
			var_sum.append(d['o'].sum())
	print "Doing update - AvgScore",avg_score,"VarSum",var_sum
env.monitor.close()
