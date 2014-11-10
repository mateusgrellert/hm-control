import os
import operator
import math
import re

class App:
	def __init__(self, valgrind = False, BDRate = False):
		if valgrind:
			self.App = 'valgrind --tool=cachegrind --log-file=valgrind.out ../JM/lencod.exe'
		else:
			self.App = '../JM_bin/lencod.exe '
		self.name = 'JM'
		self.valgrind = valgrind
		self.BDRate = BDRate
		self.numSteps = 300
		self.initConfig = '-d ../JM_bin/encoder_max_performance.cfg '

		if self.BDRate:
			self.QPs = ['20','25','30','35']
			self.makeBDRateFile()
		else:
			self.QPs = ['32']

	def makeBDRateFile(self):
		self.BDRateFile = open(self.name+'_QPWise_Values.csv','w')
		print >> self.BDRateFile, '\t'.join(self.QPs)
		self.BDRateFile.close()

	def run(self, inp, cfg, period):
		avg = []
		for i in range(len(self.getOutputNames())):
			avg.append(0)
		inp = inp.split()
		
		for qp in self.QPs:
			line = self.App + ' ' + self.initConfig + '-p Log2MaxFNumMinus4=-1 -p InputFile=/home/grellert/origCfP/cropped/' + inp[0]
			line += ' -p SourceWidth=' + inp[1] + ' -p SourceHeight=' + inp[2] + ' -p FrameRate=' + inp[3] + ' -p RDOptimization=1' + ' ' + ' '.join(cfg)
			line += ' -p IntraPeriod=30 -p FramesToBeEncoded=' + str(period)
			line += ' > JM_out.txt 2> JM_warn.txt'
			
			os.system('echo \"' + line + '\" >> cmd_line.log')
			os.system(line)
			os.system('cat JM_out.txt >> JM_out.log; cat JM_warn.txt >> JM_warn.log')
			
			out = self.parseOutput()
			for i in range(len(out)):
				avg[i] += out[i]

		return [float(x)/len(self.QPs) for x in avg]

		
	def parseOutput(self, qp):
		f = open('JM_out.txt','r')
		count = 0
		psnr_count = False

		for l in (f.readlines()):
			if 'Total encoding time' in l:
				time = float(l.split()[7])
			elif 'Y { PSNR' in l:
				y_psnr = float(l.split()[10].strip(','))
			elif 'U { PSNR' in l:
				u_psnr = float(l.split()[10].strip(','))
			elif 'V { PSNR' in l:
				v_psnr = float(l.split()[10].strip(','))
			elif 'Bit rate' in l:
				bitrate = float(l.split()[7])
		
		if self.BDRate:
			self.printBDRateFile([bitrate, y_psnr, u_psnr,v_psnr,time],qp)

		psnr = (4*y_psnr+u_psnr+v_psnr)/6.0
		if self.valgrind:
			valg = open('valgrind.out','r')
			for l in valg.readlines():
				if 'D   refs:' in l:
					rd_refs = float(l.split('(')[1].split()[0].replace(',',''))
					wr_refs = float(l.split('+')[1].split()[0].replace(',',''))
				elif 'D1  misses:' in l:
					rd_misses = float(l.split('(')[1].split()[0].replace(',',''))
					wr_misses = float(l.split('+')[1].split()[0].replace(',',''))
				elif 'LL refs' in l:
					LL_rd_refs = float(l.split('(')[1].split()[0].replace(',',''))
					LL_wr_refs = float(l.split('+')[1].split()[0].replace(',',''))
				elif 'LL misses' in l:
					LL_rd_misses = float(l.split('(')[1].split()[0].replace(',',''))
					LL_wr_misses = float(l.split('+')[1].split()[0].replace(',',''))
	
		#RDNP = self.calculatePerformance(bitrate/framesCounted, psnr/framesCounted)
		if self.valgrind:
			return [time, psnr, bitrate, rd_misses, wr_misses, LL_rd_misses, LL_wr_misses]
		else:
			return [time, psnr, bitrate]


	def printBDRateFile(self,tupl, qp):
		self.BDRateFile = open(self.name+'_QPWise_Values.csv','a')
		
		print >> self.BDRateFile, '\t'.join(tupl),'\t\t',

		if qp == self.QPs[-1]:
			print >> self.BDRateFile,'\n'
		self.BDRateFile.close()

	def calculatePerformance(self,avg_br, avg_psnr):
		weight_br = 0.5
		weight_psnr = 0.5

		norm_br = (avg_br - minMaxTable['bitrate'][0])/(minMaxTable['bitrate'][1] - minMaxTable['bitrate'][0])
		norm_psnr = (avg_psnr - minMaxTable['psnr'][0])/(minMaxTable['psnr'][1] - minMaxTable['psnr'][0])
	
		return (norm_br*weight_br+norm_psnr*weight_psnr)

	def makeParam(self,name, value):
		return ('-p ' + name + '=' + value)
	
	def splitParam(self,param):
		return (param.strip('-p ').split('='))

	def getOutputNames(self):
		if self.valgrind:
			return ['Time', 'PSNR', 'Bitrate', 'L1 RD Misses', 'L1 WR Misses','LL RD Misses', 'LL WR Misses']
		else:
			return ['Time', 'PSNR', 'Bitrate']

