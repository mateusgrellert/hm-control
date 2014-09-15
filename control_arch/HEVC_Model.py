import os
import operator
import math

class HEVC_Model:
	def __init__(self):
		self.App = '../bin/TAppEncoderStatic'

		self.period = 8
		self.stepsTaken = 0
		self.numSteps = 300
		self.initConfig = '-c ../cfg/encoder_lowdelay_main.cfg -c /home/grellert/hm-cfgs/cropped/BasketballPass.cfg --IntraPeriod=-1 '


	def run(self, config, period):
		line = self.App + ' ' + self.initConfig + config + ' --FramesToBeEncoded=' + str(period) + ' --FrameSkip=' + str(self.stepsTaken) + ' > HM_out.txt 2> HM_warn.txt'
		os.system(line)
		os.system('cat HM_out.txt >> HM_out.log')
		self.stepsTaken += period
		if self.stepsTaken > self.numSteps:
			return False
		else:
			return True

	def parseOutput(self,start=False):
		f = open('HM_out.txt','r')
		time = bitrate = psnr = framesCounted = y_psnr = u_psnr = v_psnr = 0.0

		for l in f.readlines():
			if 'B-SLICE' in l or 'P-SLICE' in l:
				tok = l.split()
				time += float(tok[tok.index('[ET')+1])
				bitrate += float(tok[tok.index('bits')-1])
				y_psnr = float(tok[tok.index('[Y')+1])
				u_psnr = float(tok[tok.index('U')+1])
				v_psnr = float(tok[tok.index('V')+1])
				psnr += (4*y_psnr+u_psnr+v_psnr)/6.0
			
				if start:
					updateMinMaxTable((4*y_psnr+u_psnr+v_psnr)/6.0, float(tok[tok.index('bits')-1]))

				framesCounted += 1.0
	
		RDNP = calculatePerformance(bitrate/framesCounted, psnr/framesCounted)

		return [time/framesCounted, RDNP]

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

