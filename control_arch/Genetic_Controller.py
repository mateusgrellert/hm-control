
class Genetic_Controller:

	def __init__(self,paramTable, App):
		self.paramTable = paramTable
		self.keys = paramTable.keys()
		self.vals = paramTable.vals()
		self.InitPopSize = 5
		self.App = App
		self.testedChromo = 0
		self.mutationRate = 0.01
		self.crossOverRate = 0.7
		buildFirstPopulation()
	
	def buildFirstPopulation(self):
		cfgs = []
		for i in range(0, self.InitPopSize):		
			cfg = []
			for v in self.vals():
				cfg_vals.append(v[random.randint(0,len(v)-1)])
			cfgs.append(cfg)
		self.population = cfgs

	def getNextCfg(self):
		if self.testedChromo < len(self.population):
			buildCfg()
			self.testedChromo += 1
		else:
			buildNewPopulation()
			self.testedChromo = 0
			buildCfg()

	def buildCfg():
		cfg = []
		for p,val in zip(self.keys,self.population[self.testedChromo]):
			cfg.append(self.App.makeParam(p, val))
		return cfg

	def buildNewPopulation():
		for p,f in zip(self.population, self.fitnessVet):
			
