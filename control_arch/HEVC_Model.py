import os
import operator
import math
import re

class App:
	def __init__(self, valgrind = False):
		if valgrind:
			self.App = 'valgrind --tool=cachegrind --log-file=valgrind.out ../bin/TAppEncoderStatic'
		else:
			self.App = '../HM_bin/TAppEncoderStatic'
		self.name = 'HM'
		self.valgrind = valgrind

		self.period = 3
		self.numSteps = 300
		self.initConfig = '-c ../cfg/encoder_lowdelay_main.cfg '
		self.QPs = ['22','27','32','37']
		self.makeBDRateFile()

	def makeBDRateFile(self):
		self.BDRateFile = open('x265_QPWise_Values.csv','w')
		print >> self.BDRateFile, '\t'.join(self.QPs)
		self.BDRateFile.close()
	
	def run(self, inp, cfg, period):
		avg = []
		for i in range(len(self.getOutputNames())):
			avg.append(0)

		for qp in self.QPs:
			line = self.App + ' ' + self.initConfig + ' -c /home/grellert/hm-cfgs/cropped/' + inp + ' ' + ' '.join(cfg)
			line += ' --IntraPeriod=-1 --FramesToBeEncoded=' + str(period) + ' --QP=' + qp
			line += ' > HM_out.txt 2> HM_warn.txt'
			os.system(line)
			os.system('cat HM_out.txt >> HM_out.log')
			out = self.parseOutput()
			for i in range(len(out)):
				avg[i] += out[i]
			self.printBDRateFile(out, qp)
			#self.stepsTaken += period
		return [float(x)/len(self.QPs) for x in avg]

	def printBDRateFile(self,tupl, qp):
		self.BDRateFile = open('x265_QPWise_Values.csv','a')
		f = open('HM_out.txt','r')
		fread = f.read()
		f.close()

		reg = 'SUMMARY.*\n.*\n.*a\s*([\d+.]+)\s*([\d+.]+)\s*([\d+.]+)\s*([\d+.]+).*\n'
		obj = re.compile(reg)
		(bitrate, y_psnr, u_psnr, v_psnr) = obj.findall(fread)[0]
		reg2 = 'Total\s*Time:\s*([\d+.]+).*'
		obj = re.compile(reg2)
		(time) = obj.findall(fread)[0]


		print >> self.BDRateFile, '\t'.join([bitrate, y_psnr, u_psnr, v_psnr,time]),'\t',
		if qp == self.QPs[-1]:
			print >> self.BDRateFile,'\n'
		self.BDRateFile.close()
		
	def parseOutput(self,start=False):
		f = open('HM_out.txt','r')
		f2 = open('HM_warn.txt','r')
		count = 0
		psnr_count = False

		for l in (f.readlines() + f2.readlines()):
			if 'Total Time' in l:
				time = float(l.split()[2])
			elif 'Bytes written to file' in l:
				bitrate = float(l.split('(')[1].split()[0])
			elif 'SUMMARY' in l:
				psnr_count = True
			elif count == 2:
				y_psnr = float(l.split()[3])
				u_psnr = float(l.split()[4])
				v_psnr = float(l.split()[5])
				psnr = (4*y_psnr+u_psnr+v_psnr)/6.0

			if psnr_count:
				count += 1

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
		return ('--' + name + '=' + value)
	
	def splitParam(self,param):
		return (param.strip('--').split('='))

	def getOutputNames(self):
		if self.valgrind:
			return ['Time', 'PSNR', 'Bitrate', 'L1 RD Misses', 'L1 WR Misses','LL RD Misses', 'LL WR Misses']
		else:
			return ['Time', 'PSNR', 'Bitrate']

