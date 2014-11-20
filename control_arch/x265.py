import os
import operator
import math
import re

class App:
	def __init__(self, valgrind = False, BDRate = False):
		if valgrind:
			self.App = 'valgrind --tool=cachegrind --log-file=valgrind.out ../x265'
		else:
			self.App = '../x265'
		self.name = 'x265'
		self.valgrind = valgrind
		self.BDRate = BDRate
		self.numSteps = 300
		self.initConfig = ' --profile main --tune psnr --psnr --no-asm --aq-mode 0 --no-scenecut'

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
		inp = inp.split()
		avg = []
		for i in range(len(self.getOutputNames())):
			avg.append(0)

		for qp in self.QPs:
			line = self.App + ' --qp ' + qp + ' --input-res ' + inp[1] + ' --fps ' + inp[2]
			line += self.initConfig + ' ' + ' '.join(cfg) + ' --frames ' + str(period) + ' ../../origCfP/' + inp[0]
			line += ' -o out.x265 > x265_out.txt 2> x265_warn.txt '

			os.system('echo \"' + line + '\" >> cmd_line.log')
			os.system(line)
			os.system('cat x265_out.txt >> x265_out.log; cat x265_warn.txt >> x265_warn.log')

			out = self.parseOutput(qp)
			for i in range(len(out)):
				avg[i] += out[i]


		return [float(x)/len(self.QPs) for x in avg]
		
	def parseOutput(self, qp):
		f = open('x265_out.txt','r')

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

		
		if self.BDRate:
			self.printBDRateFile(qp)
		#RDNP = self.calculatePerformance(bitrate/framesCounted, psnr/framesCounted)

		if self.valgrind:
			return [time, psnr, bitrate, rd_misses, wr_misses, LL_rd_misses, LL_wr_misses]
		else:
			return [time, psnr, bitrate]

	def printBDRateFile(self, qp):
		self.BDRateFile = open('x265_QPWise_Values.csv','a')
		f = open('x265_warn.txt','r')

		reg = 'global.*kb\/s\:\s*([\d+.]+).*Y\:([\d+.]+)\s*U\:([\d+.]+)\s*V\:([\d+.]+)'
		obj = re.compile(reg)
		(bitrate, y_psnr, u_psnr, v_psnr) = obj.findall(f.read())[0]

		f2 = open('x265_out.txt','r')
		reg = 'encoded.*in\s*([\d+\.]+)s'
		obj = re.compile(reg)

		(time) = obj.findall(f2.read())[0]

		print >> self.BDRateFile, '\t'.join([bitrate, y_psnr, u_psnr, v_psnr,time]),'\t\t',
		if qp == self.QPs[-1]:
			print >> self.BDRateFile,'\n',
		self.BDRateFile.close()
		
	def calculatePerformance(self,avg_br, avg_psnr):
		weight_br = 0.5
		weight_psnr = 0.5

		norm_br = (avg_br - minMaxTable['bitrate'][0])/(minMaxTable['bitrate'][1] - minMaxTable['bitrate'][0])
		norm_psnr = (avg_psnr - minMaxTable['psnr'][0])/(minMaxTable['psnr'][1] - minMaxTable['psnr'][0])
	
		return (norm_br*weight_br+norm_psnr*weight_psnr)

	def makeParam(self,name, value):
		if value:
			return ('--' + name + ' ' + value)
		else:
			return ('--' + name)
	
	def splitParam(self,param):
		ret = param.strip('--').split(' ')
		if len(ret) < 2:
			ret = ret + [0]
		return ret

	def getOutputNames(self):
		if self.valgrind:
			return ['Time', 'PSNR', 'Bitrate', 'L1 RD Misses', 'L1 WR Misses','LL RD Misses', 'LL WR Misses']
		else:
			return ['Time', 'PSNR', 'Bitrate']

