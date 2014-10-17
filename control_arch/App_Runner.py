import os
import importlib
import re
import time
import Genetic_Controller as gc

class App_Runner:

	def __init__(self, mod, configp, inputp, valgrind):
		self.config_path = configp
		self.input_path = inputp
		self.paramTable = {}
		self.paramSkip = 0
		self.lastSwitch = ''

		self.cfgVector = []
		self.switchVector = []
		self.outputVector = []
		self.sensitivityVector = []
		self.inputVet = []

		module = importlib.import_module(mod)
		self.App = module.App(valgrind)
		self.outputCsv = open(self.App.name+'_Results.csv','w')
		self.buildParamTable()
		self.makeInputVector()
		self.Controller = gc.Genetic_Controller(self.paramTable, self.App)

	def buildParamTable(self):
		f = open(self.config_path,'r')
		file_lines = f.readlines()
		self.numLevels = int(file_lines[0])
		int_conv = True
		for l in file_lines[1:]:
			if len(l) < 3: continue #skip empty lines

			param = l.split()[0]
			self.paramTable[param] = []
			if len(l.split()) > 1:
				values = l.split()[1:]

				if re.search(r'[0-9].*-[0-9].*',values[0]):
					[minv, maxv] = values[0].split('-')
					step = (float(maxv) - float(minv)*1.0)/(self.numLevels-1)
					if '.' in values[0]:
						int_conv = False
					vals = []
					for i in range(0, self.numLevels):
						val = float(minv)+i*step
						if int_conv:
							val = self.round_to(val,0.5)
						if str(val) not in vals:
							vals.append(str(val))
					self.paramTable[param] = vals

				else:
					for v in values:
						self.paramTable[param].append(v)
			else:
				self.paramTable[param] = ''

		print self.paramTable

	def makeInputVector(self):
		f = open(self.input_path,'r')

		for l in f.readlines():
			if len(l) < 3: continue #skip empty lines

			self.inputVet.append(l.strip('\n'))


	def buildFirstConfig(self):
		cfg = []
		for p in self.paramTable:
			if isinstance(self.paramTable[p], list):
				cfg.append(self.App.makeParam(p, str(self.paramTable[p][-1])))
			else:
				cfg.append(self.App.makeParam(p, ''))
		return cfg


	def sensitivityAnalysis(self, period, mode):

		cfg = self.buildFirstConfig()
		print ' '.join(cfg)
		ref_tuple = []
		out_tuple = []

		for inp in self.inputVet:
			self.App.run(inp,cfg,period)
			output = self.App.parseOutput()
			out_tuple.append(output)
			ref_tuple.append(output)

		self.outputVector.append(out_tuple)
		self.cfgVector.append(' '.join(cfg))
		self.switchVector.append('c0')

		while True:

			cfg = self.switchSingleParam(cfg, mode)
			if not(cfg): break

			print ' '.join(cfg)
			output_tuple = []
			sense_tuple = []
			for inp in self.inputVet:
				self.App.run(inp, cfg,period)
				output = self.App.parseOutput()
				output_tuple.append(output)
				sense_tuple.append(self.calcSensitivity(ref_tuple[self.inputVet.index(inp)], output))
				if mode == 'cumulative':
					ref_tuple[self.inputVet.index(inp)] = output

			self.outputVector.append(output_tuple)
			self.sensitivityVector.append(sense_tuple)

			self.cfgVector.append(' '.join(cfg))
			self.switchVector.append(self.lastSwitch)


		self.printOutput()

	def controlTarget(self, period):
		target_idx = 0
		control = self.Controller
		inp = self.inputVet[0]
		out_tuple = []
		
		cfg = self.buildFirstConfig()
		#print ' '.join(cfg)

		self.App.run(inp,cfg,period)
		output = self.App.parseOutput()
		actual = float(output[target_idx])
		SP = actual*0.4
		control.updateFitness((actual-SP)*(actual-SP))
		print '\t', SP, '\t', actual

		while (True):
			cfg = control.getNextCfg()
			#print ' '.join(cfg)
			self.App.run(inp, cfg,period)
			output = self.App.parseOutput()
			actual = float(output[target_idx])
			control.updateFitness((actual-SP)*(actual-SP))
			print '\t', SP, '\t', actual

	def switchSingleParam(self,cfg, mode):

		for pv in cfg[self.paramSkip:]:
			[p,v] = self.App.splitParam(pv)
			replace_idx = cfg.index(pv)

			for i in self.paramTable[p][::-1]:
				if self.paramTable[p].index(i) < self.paramTable[p].index(v):
					self.deltaParam = self.paramTable[p].index(i) - len(self.paramTable[p]) + 1 

					cfg[replace_idx] = self.replace_last(cfg[replace_idx], v, i)
					self.lastSwitch = p + '=' + i
				
					return cfg

			if mode == 'single':
				if isinstance(self.paramTable[p], list):
					cfg[replace_idx] = self.replace_last(cfg[replace_idx],v, self.paramTable[p][-1])
				else:
					cfg[replace_idx] = self.replace_last(cfg[replace_idx], p, '')

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
		self.cleanUp()

	def calcSensitivity(self, ref_tuple, new_tuple):
		sense_vet = []
		for a,b in zip(ref_tuple, new_tuple): 
			delta_out = (1.0-(float(b)/(float(a)*1.0)))
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
		return int(int( n/precision+correction ) * precision)


	def replace_last(self, source_string, replace_what, replace_with):
		head, sep, tail = source_string.rpartition(replace_what)
		return head + replace_with + tail

	def cleanUp(self):
		os.system('mv *log logs/')
		out_path = '_'.join([str(x) for x in time.localtime()[:5]])
		#os.system('mkdir output_'+out_path)
		#os.system('mv *csv output_'+out_path)
		os.system('rm *.out *.txt cachegrind.out* *.yuv *.bin')

			
