import os
import operator
import math

class App:
	def __init__(self, valgrind = False):
		if valgrind:
			self.App = 'valgrind --tool=cachegrind --log-file=valgrind.out ../x265'
		else:
			self.App = '../x265'
		self.valgrind = valgrind
		self.period = 8
		self.numSteps = 300
		self.initConfig = ' --profile main --tune psnr --psnr --no-asm --aq-mode 0 --no-scenecut'


	def run(self, inp, cfg, period):
		inp = inp.split()
		line = self.App + ' --input-res ' + inp[1] + ' --fps ' + inp[2] + self.initConfig + ' ' + ' '.join(cfg) + ' --frames ' + str(period) + ' ../../origCfP/cropped/' + inp[0]
		line += ' -o out.x265 > x265_out.txt 2> x265_warn.txt '
		os.system(line)
		os.system('cat x265_out.txt >> x265_out.log')
		os.system('cat x265_warn.txt >> x265_warn.log')
		#self.stepsTaken += period

		
	def parseOutput(self):
		f = open('x265_out.txt','r')
		valg = open('x265_out.txt','r')
		for l in f.readlines():
			if 'encoded' in l:
				l = l.split()
				time = float(l[4].strip('s'))
				bitrate = float(l[7])
				psnr = float(l[11])
		
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

	def calculatePerformance(self,avg_br, avg_psnr):
		weight_br = 0.5
		weight_psnr = 0.5

		norm_br = (avg_br - minMaxTable['bitrate'][0])/(minMaxTable['bitrate'][1] - minMaxTable['bitrate'][0])
		norm_psnr = (avg_psnr - minMaxTable['psnr'][0])/(minMaxTable['psnr'][1] - minMaxTable['psnr'][0])
	
		return (norm_br*weight_br+norm_psnr*weight_psnr)

	def makeParam(self,name, value):
		return ('--' + name + ' ' + value)
	
	def splitParam(self,param):
		return (param.strip('--').split(' '))

	def getOutputNames(self):
		if self.valgrind:
			return ['Time', 'PSNR', 'Bitrate', 'L1 RD Misses', 'L1 WR Misses','LL RD Misses', 'LL WR Misses']
		else:
			return ['Time', 'PSNR', 'Bitrate']

