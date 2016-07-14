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
subspace=nactions

#initialize the parameter distribution
layers=[]
layers.append({'in':observation.size,'out':subspace*4})
layers.append({'in':subspace*4,'out':subspace})
layers.append({'in':subspace,'out':nactions})

#initialize the network
for d in layers:
	d['u']=np.zeros(d['in']*d['out'])
	d['o']=np.ones(d['in']*d['out'])

for bi in xrange(big_its):
	#sample the parameters for ech layer
	for d in layers:
		d['params'] = np.random.multivariate_normal(d['u'], np.diag(d['o']), small_its).reshape(small_its,d['in'],d['out']) 
	rewards = []
	avg_score=0
	#run for each small iteration
	for i in xrange(small_its):
		reward=[]
		reward_total=0
		old_action = np.zeros(nactions)
		while True:
			l=observation
			for d in layers:
				l=np.dot(l,d['params'][i])
				#l=(l * (l>0)) # ReLU
				l=np.tanh(l) # sigmoid
				#l=np.sin(l) # wtf??
			action=np.clip(l,-1,1) # clip the output values to make sure its in the range
			old_action=action # save the old action as input to next step
			observation, reward_f, done, _ = env.step(action) # do a step in openAI
			reward.append(reward_f) # keep track of the reward for each step
			if done: # if the simulation is done - out of bounds, or out of time
			    observation = env.reset() # reset to a new training episode
			    break # while true doesnt break easy...
		avg_score+=sum(reward)/float(small_its) # the average score per episode
		rewards.append((reward_total,i)) # put the score and which example it was into a list
	#sort the list by the score, so that the best ones are at the end
	rewards.sort()
	#Only keep the 'elite' fraction
	rewards=rewards[int(len(rewards)*(1-keep)):]
	#update each layers distribution
	var_sum=[]
	for d in layers:
		values=np.zeros((len(rewards),d['in'],d['out']))
		weights=np.zeros(len(rewards))
		average = np.average(values,0).flatten()
		variance = np.var(values,0).flatten()
		d['u']=d['u']*0.5+0.5*average
		d['o']=d['o']*0.5+0.5*variance
		var_sum.append(d['o'].sum())
	print "Doing update - AvgScore",avg_score,"VarSum",var_sum
env.monitor.close()
