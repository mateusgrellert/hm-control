import os
import operator

def run(binary, config, period):
	global stepsTaken
	initConfig = '-c ../cfg/encoder_randomaccess_main.cfg -c /home/grellert/hm-cfgs/cropped/BQSquare.cfg --IntraPeriod=-1 '

	#print  (binary + ' ' + config + ' --FramesToBeEncoded=' + str(period) + ' --FrameSkip=' + str(stepsTaken) + ' > HM_out.txt')
	os.system(binary + ' ' + initConfig + config + ' --FramesToBeEncoded=' + str(period) + ' --FrameSkip=' + str(stepsTaken) + ' > HM_out.txt 2> dummy.txt')
	os.system('cat HM_out.txt >> HM_out.log')
	stepsTaken += period
	if stepsTaken > numSteps:
		return True
	else:
		return False


def parseOutput(start=False):
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
	
	#print '## Avg. Outputs:\n\tPSNR: ',psnr/framesCounted, '\tbitrate: ', bitrate/framesCounted,
	#print '\tRDNP :', calculatePerformanceFactor(bitrate/framesCounted, psnr/framesCounted), '\tTime:', time/framesCounted
	
	RDNP = calculatePerformanceFactor(bitrate/framesCounted, psnr/framesCounted)
	#print ("%.2f" % (time/framesCounted))
	return [time/framesCounted, RDNP]

def updateMinMaxTable(psnr, bitrate):
	global minMaxTable

	minMaxTable['psnr'][0] = min(psnr, minMaxTable['psnr'][0])
	minMaxTable['psnr'][1] = max(psnr, minMaxTable['psnr'][1])
	minMaxTable['bitrate'][0] = min(bitrate, minMaxTable['bitrate'][0])
	minMaxTable['bitrate'][1] = max(bitrate, minMaxTable['bitrate'][1])
	
	#print '## MinMax table values:\n\tPSNR:', minMaxTable['psnr'][0] , ' ' , minMaxTable['psnr'][1] 
	#print '\tbitrate:', minMaxTable['bitrate'][0] , ' ' , minMaxTable['bitrate'][1] 

def calculatePerformanceFactor(avg_br, avg_psnr):
	weight_br = 0.5
	weight_psnr = 0.5

	norm_br = (avg_br - minMaxTable['bitrate'][0])/(minMaxTable['bitrate'][1] - minMaxTable['bitrate'][0])
	norm_psnr = (avg_psnr - minMaxTable['psnr'][0])/(minMaxTable['psnr'][1] - minMaxTable['psnr'][0])
	
	return (norm_br*weight_br+norm_psnr*weight_psnr)

def getConfigs():
	f = open('configs.inp','r')
	cfgs = {}
	for l in f.readlines():
		param = l.split()[0]
		cfgs[param] = l.split()[1:] + [ -1.0, -1.0] # max min step comp RDNP
	return cfgs

def wrapUp():
	#os.system('rm -rf logs; mkdir logs')
	#os.system('mv *.log logs')
	os.system('sh cleanup.sh')



def addParam(config, curr_param, params):
	[maxv, minv, step] = params[curr_param][:3]
	val = str(int(maxv) - int(step))
	config = config + ' ' + ('--' + curr_param + '=' + val)
	return config

def scaleUp(config, curr_param, params):
	tokens = config.split()
	[maxv, minv, step] = params[curr_param][:3]
	new_config = ''

	for t in tokens:
		if curr_param in t:
			val = int(t.split('=')[1])
			if val < int(maxv):
				val += int(step)
			t = t.split('=')[0] + '=' + str(val)
		new_config = new_config + ' ' + t
	return new_config


def removeParam(config, curr_param, params):
	tokens = config.split()
	new_config = ''
	for t in tokens:
		if curr_param not in t:
			new_config = new_config + ' ' + t

	return new_config

def scaleDown(config, curr_param, params):
	tokens = config.split()
	[maxv, minv, step] = params[curr_param][:3]
	new_config = ''

	for t in tokens:
		if curr_param in t:
			val = int(t.split('=')[1])
			if val > int(minv):
				val -= int(step)
			t = t.split('=')[0] + '=' + str(val)
		new_config = new_config + ' ' + t
	return new_config


def switchParam(config, curr_param, params):
	tokens = config.split()
	new_config = ''

	for p, val in params.items():
		if val[-1] == -1.0:
				config = addParam('', p, params)
				return [config, p]


	for t in tokens:
		if curr_param in t:
			for p, val in params.items():
				if val[-1] == -1.0:
					switch = p
					t = '--' + p + '=' + str(int(val[0]) - int(val[2]))

		new_config = new_config + ' ' + t
	return [new_config, switch]

def updateParamTable(params, curr_param, comp, RDNP):
	params[curr_param][-2:] = [comp, RDNP]

def getBestRDNP(params):
	return sorted(params.items(), key=lambda x: x[1][-1], reverse=True)

def getWorstRDNP(params):
	return sorted(params.items(), key=lambda x: x[1][-1])

def notFullyTrained(params):
	for p,val in params.items():
		if val[-1] == -1.0:
			return True

	return False

## Controller Setup for HEVC Model Simulation #####
App = './TAppEncoderStatic'

initialPeriod = 8
testingPeriod = 8
runningPeriod = 8
stepsTaken = 0
numSteps = 240

## Helping Data Structures for Normalization #####
minMaxTable = {'psnr' : [99999999.0, -1.0], 'bitrate' : [99999999.0, -1.0]}



