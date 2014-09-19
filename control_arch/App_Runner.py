import os
import importlib

class App_Runner:

	def __init__(self, mod, configp, inputp):
		self.config_path = configp
		self.input_path = inputp
		self.paramTable = {}
		self.paramSkip = 0
		self.lastSwitch = ''
		self.outputCsv = open('App_Runner_Results.csv','w')
		self.cfgVector = []
		self.switchVector = []
		self.outputVector = []
		self.sensitivityVector = []
		self.inputVet = []

		module = importlib.import_module(mod)
		self.App = module.App()

		self.buildParamTable()
		self.makeInputVector()

	def buildParamTable(self):
		f = open(self.config_path,'r')
		file_lines = f.readlines()
		self.numLevels = int(file_lines[0])
		for l in file_lines[1:]:
			if len(l) < 3: continue #skip empty lines

			param = l.split()[0]
			self.paramTable[param] = []
			values = l.split()[1:]

			if '-' in values[0]:
				[minv, maxv] = values[0].split('-')
				step = (int(maxv) - int(minv)*1.0)/(self.numLevels-1)

				vals = []
				for i in range(0, self.numLevels):
					val = int(minv)+i*step
					val = int(self.round_to(val,0.5))
					vals.append(str(val))
				self.paramTable[param] = vals

			else:
				for v in values:
					self.paramTable[param].append(v)

		print self.paramTable

	def makeInputVector(self):
		f = open(self.input_path,'r')

		for l in f.readlines():
			if len(l) < 3: continue #skip empty lines

			self.inputVet.append(l.strip('\n'))


	def buildFirstConfig(self):
		cfg = []
		for p in self.paramTable:
			cfg.append(self.App.makeParam(p, str(self.paramTable[p][-1])))
		return cfg


	def sensitivityAnalysis(self, period, mode):

		cfg = self.buildFirstConfig()
		print ' '.join(cfg)
		ref_tuple = []

		for inp in self.inputVet:
			self.App.run(inp,cfg,period)
			ref_tuple.append(self.App.parseOutput())

		self.outputVector.append(ref_tuple)
		self.cfgVector.append(cfg)
		self.switchVector.append('c0')

		while True:

			cfg = self.switchSingleParam(cfg, mode)
			if not(cfg): break

			print ' '.join(cfg)
			output_tuple = []
			sense_tuple = []
			for inp in self.inputVet:
				self.App.run(inp, cfg,period)
				output_tuple.append(self.App.parseOutput())
				sense_tuple.append(self.calcSensitivity(ref_tuple[self.inputVet.index(inp)], self.App.parseOutput()))

			self.outputVector.append(output_tuple)
			self.sensitivityVector.append(sense_tuple)

			self.cfgVector.append(' '.join(cfg))
			self.switchVector.append(self.lastSwitch)


		self.printOutput()



	def switchSingleParam(self,cfg, mode):

		for pv in cfg[self.paramSkip:]:
			[p,v] = self.App.splitParam(pv)
			replace_idx = cfg.index(pv)

			for i in self.paramTable[p][::-1]:
				if self.paramTable[p].index(i) < self.paramTable[p].index(v):
					if i.isdigit():
						self.deltaParam = 1.0-(int(i)/(self.paramTable[p][-1]*1.0))
					else:
						self.deltaParam = 1.0/self.numLevels

					cfg[replace_idx] = cfg[replace_idx].replace(v, i, 1)
					self.lastSwitch = p + '=' + i
				
					return cfg

			if mode == 'single':
				cfg[replace_idx] = cfg[replace_idx].replace(v, self.paramTable[p][-1], 1)

			self.paramSkip += 1
		return False
			

	def printOutput(self):

		self.reportOutput()
		print >> self.outputCsv, '\n'*3
		self.reportSensitivity()
		print >> self.outputCsv, '\n'*10
		
		count = 0
		for cfg in self.cfgVector:
			print >> self.outputCsv, 'c'+str(count)+'\t',cfg
			count += 1


	def calcSensitivity(self, ref_tuple, new_tuple):
		sense_vet = []
		for a,b in zip(ref_tuple, new_tuple): 
			delta_out = (1.0-(b/(a*1.0)))
			sense_vet.append(delta_out)

		return sense_vet

	def printCsvHeader(self):
		outputNames = self.App.getOutputNames()

		for inp in self.inputVet:
			print >> self.outputCsv,'\t'+ inp +'\t'*(len(outputNames)-1),

		print >> self.outputCsv,'\n',
			
		for inp in self.inputVet:
			for name in outputNames:
				print >> self.outputCsv,'\t'+ name,

	def reportSensitivity(self):
		self.printCsvHeader()

		for cfg, cfg_out in zip(self.switchVector[1:], self.sensitivityVector):
			print >> self.outputCsv, '\n'+cfg+'\t',
			for seq in cfg_out:
				for o in seq:
					print >> self.outputCsv, ("%.2f" % o),'\t',


	def reportOutput(self):

		self.printCsvHeader()
		for cfg,cfg_out in zip(self.switchVector, self.outputVector):
			print >> self.outputCsv, '\n'+cfg+'\t',
			for seq in cfg_out:
				for o in seq:
					print >> self.outputCsv, ("%.2f" % o),'\t',


	def round_to(self,n, precision):
		correction = 0.5 if n >= 0 else -0.5
		return int( n/precision+correction ) * precision

			
