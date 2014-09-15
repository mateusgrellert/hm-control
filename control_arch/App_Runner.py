from HEVC_Model import *
import os

class App_Runner:

	def __init__(self):
		self.numLevels = 4
		self.paramTable = {}
		self.App = HEVC_Model()
		self.buildParamTable()
		self.paramSkip = 0
		self.outputCsv = open('App_Runner_Results.csv','w')
		self.outputHash = {}

	def buildParamTable(self):
		f = open('configs.inp','r')


		for l in f.readlines():
			if len(l) < 3: continue #skip empty lines

			[param, minv, maxv] = l.split()
			step = (int(maxv) - int(minv)*1.0)/(self.numLevels-1)

			vals = []
			for i in range(0, self.numLevels):
				val = (int(minv)+i*step)
				val = (int(round(val,0)))
				vals.append(val)

			self.paramTable[param] = vals

	def buildFirstConfig(self):
		cfg = ''
		for p in self.paramTable:
			cfg += self.App.makeParam(p, str(self.paramTable[p][-1])) + ' '
		return cfg

	def singleSwitchSensitivityAnalysis(self, period):
		cfg = self.buildFirstConfig()

		while cfg and self.App.run(cfg,period):
			print cfg
			output_tuple = App.parseOutput()
			self.outputHash[cfg] = output_tuple
			cfg = self.switchSingleParam(cfg)

		self.printOutput(cfg, output_tuple, count)

	def switchSingleParam(self,cfg):
		params_values = cfg.split()[self.paramSkip:]
		for pv in params_values:
			[p,v] = self.App.splitParam(pv)
			p_idx = cfg.index(p)
			for i in self.paramTable[p][::-1]:
				if i < int(v):
					cfg = cfg[:p_idx] + cfg[p_idx:].replace(v, str(i), 1)
					return cfg
			cfg = cfg[:p_idx] + cfg[p_idx:].replace(v, str(self.paramTable[p][-1]), 1)
			self.paramSkip += 1
			
	def printOutput(self, cfg, out_tuple, cfg_id):
		for cfg self.outputHash
		print >> self.outputCsv, 'c'+cfg_id+';',
		for o in out_tuple:
			print o,';'
		print 

