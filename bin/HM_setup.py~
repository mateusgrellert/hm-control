import os

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

def getParameters():
	f = open('configs.inp','r')
	params = []
	for l in f.readlines():
		params.append(l.split()[0])

	f.close()
	return params

def getMinMaxStep(param):
	f = open('configs.inp','r')
	for l in f.readlines():
		if param in l:
			f.close()
			return l.split()[1:]

def wrapUp():
	#os.system('rm -rf logs; mkdir logs')
	#os.system('mv *.log logs')
	os.system('sh cleanup.sh')



def combineConfigs(param,config):
	[minv, maxv, step] = getMinMaxStep(param)
	config = '--' + param + '='+ maxv + ' ' + config
	config = ' '.join(sorted(config.split()))
	return config

def splitConfig(config):
	config = ' '.join(config.split()[:-1])
	return config

def downScaleParameters(config):
	values = config.split()
	while(n_tries < len(values):
		n_tries += 1
		i =  math.randint(0,len(values)-1)
		[par,val] = values[i].split('=')
		[minv, maxv, step] = getMinMaxStep(par.strip('--'))
		if val > minv:
			val = str(int(val) - int(step))
			values[i] = par + '=' + val
			return ' '.join(values)
	return ' '.join(values)
	
def upScaleParameters(config):
	values = config.split()
	while(n_tries < len(values):
		n_tries += 1
		i =  math.randint(0,len(values)-1)
		[par,val] = values[i].split('=')
		[minv, maxv, step] = getMinMaxStep(par.strip('--'))
		if val < maxv:
			val = str(int(val) + int(step))
			values[i] = par + '=' + val
			return ' '.join(values)
	return ' '.join(values)


## Controller Setup for HEVC Model Simulation #####
App = './TAppEncoderStatic'

initialPeriod = 8
testingPeriod = 8
runningPeriod = 8
stepsTaken = 0
numSteps = 240

## Helping Data Structures for Normalization #####
minMaxTable = {'psnr' : [99999999.0, -1.0], 'bitrate' : [99999999.0, -1.0]}
configurationMap = {}



