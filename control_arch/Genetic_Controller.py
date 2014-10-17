import random


class Genetic_Controller:

	def __init__(self,paramTable, App):
		self.paramTable = paramTable
		self.keys = paramTable.keys()
		self.vals = paramTable.values()
		self.InitPopSize = 10
		self.popSize = 8
		self.App = App
		self.testedChromo = 0
		self.mutationRate = 1
		self.crossOverRate = 7
		self.buildFirstPopulation()

	
	def buildFirstPopulation(self):
		cfgs = []
		for i in range(0, self.InitPopSize):		
			cfg_vals = []
			for v in self.vals:
				cfg_vals.append(v[random.randint(0,len(v)-1)])
			cfgs.append(cfg_vals)
		self.population = cfgs
		self.buildFitnessVet()

	def buildFitnessVet(self):
		self.fitnessVet = []
		for i in range(0, len(self.population)):		
				self.fitnessVet.append(0)

	def getNextCfg(self):
		if self.testedChromo >= len(self.population):
			self.buildNewPopulation()
			
			self.testedChromo = 0

		cfg = self.buildCfg()
		self.testedChromo += 1
		return cfg

	def buildCfg(self):
		cfg = []
		for p,val in zip(self.keys,self.population[self.testedChromo]):
			cfg.append(self.App.makeParam(p, val))
		return cfg

	def buildNewPopulation(self):
		new_population = []
		pair = []
		self.makeFitnessVet()
		selected = 0
		while len(new_population) < self.popSize:
			for p,f in zip(self.population, self.fitnessVet):
				rand = self.getRandom()
				if  rand <= f and selected < 2:
					pair.append(p)
					selected += 1
				if selected == 2:
					x = pair[0]
					y = pair[1]
					selected = 0
					pair = []
					if self.getRandom() <= self.crossOverRate:
						pos = random.randint(0,len(x)-1)
						for i in range(pos, len(x)):
							tmp = x[i]
							x[i] = y[i]
							y[i] = tmp
						for i in range(0, len(x)):
							if self.getRandom() <= self.mutationRate:
								x[i] = self.vals[i][random.randint(0,len(self.vals[i])-1)]
						for i in range(0, len(x)):
							if self.getRandom() <= self.mutationRate:
								y[i] = self.vals[i][random.randint(0,len(self.vals[i])-1)]
					x = '\t'.join(x)
					y = '\t'.join(y)
					if x not in new_population:
						new_population.append(x)
					if y not in new_population:
						new_population.append(y)


		self.population = []
		for p in new_population[:self.popSize]:
			self.population.append(p.split('\t'))
		self.buildFitnessVet()

	def updateFitness(self,value):
		self.fitnessVet[self.testedChromo-1] = value

	def makeFitnessVet(self):
		fit = []
		for i in range (0, len(self.fitnessVet)):
			f = 1.0-(self.fitnessVet[i]*1.0/max(self.fitnessVet))
			fit.append(f*100)
		self.fitnessVet = fit
		#for p, f in zip(self.population, self.fitnessVet):
			#print p,'\t',f

	def getRandom(self):
		return random.randint(0,100)
