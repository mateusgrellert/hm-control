from HM_setup import *
import os

def initialPhase(App, initialPeriod):
	print '## Starting Phase ###'

	run(App, ' ', initialPeriod)
	[initComputation, RDNP] = parseOutput(start=True)

	#print '\tInital Time: ',  ("%.2f" % initComputation), '\tRDNP: ',  ("%.2f" % RDNP)
	return [initComputation, RDNP]

def testingPhase(App, testingPeriod, targetComputation, currComp):
	print '## Testing Phase ###'
	bestComputation = 999999
	bestRDNP = -1.0
	acum_config =  ''
	
	negative_tol = 0.9
	positive_tol = 1.1

	paramLUT = buildParamLUT()
	configs = {}
	increase_comp = (targetComputation > currComp)
	decrease_comp = not(increase_comp)
	stable = False
	runComp = False
	config = ''
	old_config = ''
	prev_comp = currComp

	while (not runComp):
		best_params = getBestRDNP(paramLUT)
		worst_params = getWorstRDNP(paramLUT)
		idx = 0

		while increase_comp:
			increase_comp = False
			curr_param = worst_params[idx]

			if curr_param in old_config:
				config = removeParam(old_config, curr_param, paramLUT)
			elif notFullyTrained(paramLUT):
				curr_param = getWorstRDNP(paramLUT)
				[config, curr_param] = switchParam(old_config, curr_param, paramLUT)
			else:
				config = scaleUp(old_config, curr_param, paramLUT)
				if config == old_config:
					increase_comp = True
			idx += 1

		while decrease_comp:
			decrease_comp = False
			curr_param = best_params[idx]

			if curr_param not in old_config:
				config = addParam(old_config, curr_param, paramLUT)
			elif notFullyTrained(paramLUT):
				curr_param = getWorstRDNP(paramLUT)
				[config, curr_param] = switchParam(old_config, curr_param, paramLUT)
			else:
				config = scaleDown(old_config, curr_param, paramLUT)
				if config == old_config:
					decrease_comp = True
			idx += 1			


		if notFullyTrained(paramLUT) and not stable:
			period = testingPeriod
		else:
			period = testingPeriod

		runComp = run(App, config, period)

		config = ' '.join(sorted(config.split()))
		[comp, RDNP] = parseOutput()

		deltaT = comp/prev_comp*1.0

		updateParamTable(paramLUT, curr_param, config, deltaT, RDNP)
		updateConfigsTable(configs, config, comp, RDNP)

		#print ('%.2f\t%.2f\t%d\t%.2f' % (comp,targetComputation,period, RDNP))
		
		increase_comp = False
		decrease_comp = False
		old_config = config
		prev_comp = comp
		prev_RDNP = RDNP

		if (comp) <= targetComputation*negative_tol:
			increase_comp = True
		elif (comp) >= targetComputation*positive_tol:
			decrease_comp = True
		stable = not(increase_comp) and not(decrease_comp)

	printRDNP(params)
	return


def updateParamTable(params, curr_param, config, deltaT, RDNP):
	val = getParamValueInConfig(config)
	params[curr_param][val] = [deltaT, RDNP]

def updateConfigsTable(configs, config, comp, RDNP):
	if config not in configs.keys():
		configs[config] = [comp, RDNP]
		print ('%s\t%.2f\t%.2f' % (config, comp, RDNP))

def getBestRDNP(params):
	sort = sorted(params.items(), key=lambda x: x[1].items()[1][-1][-1], reverse=True)
	vet = []
	for s in sort:
		vet.append(s[0])
	return vet

def getWorstRDNP(params):
	sort = sorted(params.items(), key=lambda  x: x[1].items()[1][-1][-1])
	vet = []
	for s in sort:
		vet.append(s[0])
	return vet

def notFullyTrained(params):
	for p,val in params.items():
		if val[-1] == -1.0:
			return True

	return False

def printRDNP(params):
	for k,val in params.items():
		print ("%s\t%.2f\n" % (k, val[-1]) )






[initComputation, RDNP] = initialPhase(App, initialPeriod)
targetComputation = initComputation*0.6
	
print ('%.2f\t%.2f\t%d\t%.2f' % (initComputation,targetComputation,initialPeriod, RDNP))

testingPhase(App,testingPeriod, targetComputation, initComputation)

wrapUp()

