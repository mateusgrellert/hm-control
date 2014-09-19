import os
import operator
import math

class App:
	def __init__(self):
		self.App = '../x265'

		self.period = 8
		self.numSteps = 300
		self.initConfig = '--preset placebo --tune psnr --no-asm --aq-mode 0 --no-scenecut'


	def run(self, inp, cfg, period):
		line = self.App + ' --input-res ' + inp[1] + ' ' + self.initConfig + ' ' + ' '.join(cfg) + ' -o out.x265 ../../origCfP/cropped/' + inp[0]
		line += ' --frames ' + str(period)
		line += ' 2> x265_out.txt '
		os.system(line)
		os.system('cat x265_out.txt >> x265_out.log')
		#self.stepsTaken += period

		
	def parseOutput(self):
		f = open('x265_out.txt','r')

		last3_lines = f.readlines()[-3:]
		psnr_line = last3_lines[0]
		time_bitrate_line = last3_lines[2]
		n_frames = int(time_bitrate_line.split()[1])
		fps = float(time_bitrate_line.split()[3])
		bitrate = float(time_bitrate_line.split()[5])
		for t in psnr_line.split():
			if 'Y:' in t:
				y_psnr = float(t.split(':')[-1])
			elif 'U:' in t:
				u_psnr = float(t.split(':')[-1])
			elif 'V:' in t:
				v_psnr = float(t.split(':')[-1])
			
		psnr = (4*y_psnr+u_psnr+v_psnr)/6.0
		time = n_frames/fps	
	
		#RDNP = self.calculatePerformance(bitrate/framesCounted, psnr/framesCounted)

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
		return ['Time', 'PSNR', 'Bitrate']

