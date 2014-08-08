from HM_setup import *
import os

def initialPhase(App, initialPeriod):
	print '## Starting Phase ###'

	run(App, ' --SearchRange = 128 --BipredSearchRange=8 ', initialPeriod)
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

	params = getConfigs()
	configs = {}
	increase_comp = False
	stable = False
	decrease_comp = True
	runComp = False
	config = ''
	old_config = ''

	while (not runComp):
		best_params = getBestRDNP(params)
		worst_params = getWorstRDNP(params)
		idx = 0

		while increase_comp:
			increase_comp = False
			curr_param = worst_params[idx][0]

			if curr_param in old_config:
				config = removeParam(old_config, curr_param, params)
			elif notFullyTrained(params):
				curr_param = getWorstRDNP(params)
				[config, curr_param] = switchParam(old_config, curr_param, params)
			else:
				config = scaleUp(old_config, curr_param, params)
				if config == old_config:
					increase_comp = True
			idx += 1

		while decrease_comp:
			decrease_comp = False
			curr_param = best_params[idx][0]

			if curr_param not in old_config:
				config = addParam(old_config, curr_param, params)
			elif notFullyTrained(params):
				curr_param = getWorstRDNP(params)
				[config, curr_param] = switchParam(old_config, curr_param, params)
			else:
				config = scaleDown(old_config, curr_param, params)
				if config == old_config:
					decrease_comp = True
			idx += 1			


		if notFullyTrained(params) and not stable:
			period = testingPeriod
		else:
			period = testingPeriod

		runComp = run(App, config, period)

		config = ' '.join(sorted(config.split()))
		[comp, RDNP] = parseOutput()
		updateParamTable(params, curr_param, comp, RDNP)
		updateConfigsTable(configs, config, comp, RDNP)

		#print ('%.2f\t%.2f\t%d\t%.2f' % (comp,targetComputation,period, RDNP))
		
		increase_comp = False
		decrease_comp = False
		old_config = config

		if (comp) <= targetComputation*negative_tol:
			increase_comp = True
		elif (comp) >= targetComputation*positive_tol:
			decrease_comp = True
		stable = not(increase_comp) and not(decrease_comp)

	printRDNP(params)
	return


def updateParamTable(params, curr_param, comp, RDNP):
	params[curr_param][-2:] = [comp, RDNP]

def updateConfigsTable(configs, config, comp, RDNP):
	if config not in configs.keys():
		configs[config] = [comp, RDNP]
		print ('%s\t%.2f\t%.2f' % (config, comp, RDNP))

def getBestRDNP(params):
	return sorted(params.items(), key=lambda x: x[1][-1], reverse=True)

def getWorstRDNP(params):
	return sorted(params.items(), key=lambda x: x[1][-1])

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

