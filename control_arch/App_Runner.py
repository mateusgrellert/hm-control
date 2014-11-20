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



		self.inputVet = []

		module = importlib.import_module(mod)
		self.App = module.App(valgrind, False)
		self.outputCsv = open(self.App.name+'_Results.csv','w')
		self.outputCsv.close()

		self.buildParamTable()
		self.makeInputVector()
		#self.Controller = gc.Genetic_Controller(self.paramTable, self.App)



	def preparateTempFiles(self):
		cfgFile = open('AppRunner_cfg','w')
		switchFile = open('AppRunner_switch','w')
		outputFile = open('AppRunner_output','w')
		sensitivityFile = open('AppRunner_sense','w')

		cfgFile.close()
		switchFile.close()
		outputFile.close()
		sensitivityFile.close()



	def buildParamTable(self):
		f = open(self.config_path,'r')
		file_lines = f.readlines()
		f.close()
		self.paramTable["SWITCHES_ON"] = []
		self.paramTable["SWITCHES_OFF"] = []

		for line in file_lines:
			if len(line) <= 1: continue # skip empty lines
			if '#' in line: continue # skip comments

			if ':' in line: # param : 1 2 3 ...
				[param, vals] = line.split(':')
				param = param.strip(' ')
				self.paramTable[param] = []
				for v in vals.split():
					self.paramTable[param].append(v)

			elif '/' in line: # SWITCH OFF/SWITCH ON
				[sw1, sw2] = line.split('/')
				self.paramTable["SWITCHES_OFF"].append(sw1.strip('\n'))
				self.paramTable["SWITCHES_ON"].append(sw2.strip('\n'))

		self.printParamTable()




	def printParamTable(self):
		for k,v in self.paramTable.items():
			print k, ' : ', v




	def makeInputVector(self):
		f = open(self.input_path,'r')

		for l in f.readlines():
			if len(l) <= 1: continue # skip empty lines

			self.inputVet.append(l.strip('\n'))



	def buildFirstConfig(self):
		cfg = []
		for p,vals in self.paramTable.items():
			if p == 'SWITCHES_ON':
				for switch in vals:
					cfg.append(self.App.makeParam(switch, ''))
			elif p != 'SWITCHES_OFF':
				cfg.append(self.App.makeParam(p, vals[-1]))
		return cfg




	def sensitivityAnalysis(self, period, mode):
		self.preparateTempFiles()

		self.lastSwitch = 'c0'
		cfg = self.buildFirstConfig()
		ref_tuple = []
		for i in range(len(self.inputVet)):
			ref_tuple.append(0)

		while cfg:
			output_tuple = []
			sense_tuple = []
			print ' '.join(cfg)
			for i in range(len(self.inputVet)):
				inp = self.inputVet[i]

				output = self.App.run(inp, cfg,period)
				output_tuple.append(output)
				if self.lastSwitch != 'c0':
					sense_tuple.append(self.calcSensitivity(ref_tuple[i], output))

				if (self.lastSwitch == 'c0' or mode == 'cumulative'): # update reference results if first run or if cumulative analysis
					ref_tuple[i] = output

			self.saveTempResults(output_tuple, sense_tuple, cfg)

			
			cfg = self.switchSingleParam(cfg, mode)

		self.printOutput()



	def saveTempResults(self, output_tuple, sense_tuple, cfg):
		cfgFile = open('AppRunner_cfg','a')
		switchFile = open('AppRunner_switch','a')
		outputFile = open('AppRunner_output','a')
		sensitivityFile = open('AppRunner_sense','a')


		print >> outputFile, ';'.join([(','.join([str(y) for y in x])) for x in output_tuple])
		print >> sensitivityFile, ';'.join([(','.join([str(y) for y in x])) for x in sense_tuple])
		
		print >> cfgFile, ' '.join(cfg)
		print >> switchFile, self.lastSwitch

		cfgFile.close()
		switchFile.close()
		outputFile.close()
		sensitivityFile.close()




	def controlTarget(self, period):
		target_idx = 0
		control = self.Controller
		inp = self.inputVet[0]
		out_tuple = []
		
		cfg = self.buildFirstConfig()

		output = self.App.run(inp,cfg,period)
		actual = float(output[target_idx])
		SP = actual*0.4
		control.updateFitness((actual-SP)*(actual-SP))
		print '\t', SP, '\t', actual

		while (True):
			cfg = control.getNextCfg()
			output = self.App.run(inp, cfg,period)
			actual = float(output[target_idx])
			control.updateFitness((actual-SP)*(actual-SP))
			print '\t', SP, '\t', actual



	def switchSingleParam(self,cfg, mode):

		for pv in cfg[self.paramSkip:]:
			[p,v] = self.App.splitParam(pv)
			replace_idx = cfg.index(pv)
			
			if p in self.paramTable['SWITCHES_ON']:
				p_idx = self.paramTable['SWITCHES_ON'].index(p)
				sw_off = self.paramTable['SWITCHES_OFF'][p_idx]
				cfg[replace_idx] = self.replace_last(cfg[replace_idx], p, sw_off)
				self.lastSwitch = sw_off
				return cfg
			if p not in self.paramTable['SWITCHES_OFF']:
				for i in self.paramTable[p][::-1]:
					if self.paramTable[p].index(i) < self.paramTable[p].index(v):
						self.deltaParam = self.paramTable[p].index(i) - len(self.paramTable[p]) + 1 

						cfg[replace_idx] = self.replace_last(cfg[replace_idx], v, i)
						self.lastSwitch = p + '=' + i
				
						return cfg

			if mode == 'single':
				if p in self.paramTable['SWITCHES_OFF']:
					p_idx = self.paramTable['SWITCHES_OFF'].index(p)
					sw_on = self.paramTable['SWITCHES_ON'][p_idx]
					cfg[replace_idx] = self.replace_last(cfg[replace_idx], p, sw_on)
				else:
					cfg[replace_idx] = self.replace_last(cfg[replace_idx],v, self.paramTable[p][-1])

			self.paramSkip += 1
		return False
			

	def printOutput(self):
		self.outputCsv = open(self.App.name+'_Results.csv','a')
		self.reportOutput()
		print >> self.outputCsv, '\n'*3
		self.reportSensitivity()
		print >> self.outputCsv, '\n'*10
		
		count = 0
		cfgVector = self.makeVectorFromFile('AppRunner_cfg')

		for cfg in cfgVector:
			print >> self.outputCsv, 'c'+str(count)+'\t',cfg
			count += 1
		self.cleanUp()
		self.outputCsv.close()

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

		switchVector = self.makeVectorFromFile('AppRunner_switch')
		sensitivityVector = self.makeVectorFromFile('AppRunner_sense')

		for cfg, cfg_out in zip(switchVector[1:], sensitivityVector[1:]):
			print >> self.outputCsv, '\n'+cfg+'\t',
			for seq in cfg_out:
				for o in seq:
					print >> self.outputCsv, ("%.2f" % float(o)),'\t',



	def makeVectorFromFile(self,path):
		f = open(path, 'r')
		vet = []
		for l in f.readlines():
			row = []
			l = l.strip('\n')
			if ';' in l:
				for i in l.split(';'):
					row.append(i.split(','))
			else:
				if ',' in l:
					row.append(l.split(','))
				else:
					row = l
			vet.append(row)
		return vet



	def reportOutput(self):
		switchVector = self.makeVectorFromFile('AppRunner_switch')
		outputVector = self.makeVectorFromFile('AppRunner_output') 

		self.printCsvHeader()
		for cfg,cfg_out in zip(switchVector, outputVector):
			print >> self.outputCsv, '\n'+cfg+'\t',
			for seq in cfg_out:
				for o in seq:
					print >> self.outputCsv, ("%.2f" % float(o)),'\t',


	def round_to(self,n, precision):
		correction = 0.5 if n >= 0 else -0.5
		return int(int( n/precision+correction ) * precision)


	def replace_last(self, source_string, replace_what, replace_with):
		head, sep, tail = source_string.rpartition(replace_what)
		return head + replace_with + tail

	def cleanUp(self):
		os.system('mv *log logs/')
		#out_path = '_'.join([str(x) for x in time.localtime()[:5]])
		#os.system('mkdir output_'+out_path)
		#os.system('mv *csv output_'+out_path)
		os.system('rm -rf *.out *.txt cachegrind.out* *.yuv *.bin')

			
