from HM_setup import *
import os

def initialPhase(App, initialPeriod):
	print '## Starting Phase ###'

	run(App, ' --SearchRange = 128 --BipredSearchRange=8 ', initialPeriod)
	[initComputation, RDNP] = parseOutput(start=True)

	#print '\tInital Time: ',  ("%.2f" % initComputation), '\tRDNP: ',  ("%.2f" % RDNP)
	return initComputation

def testingPhase(App, testingPeriod, targetComputation, currComp):
	print '## Testing Phase ###'
	bestComputation = 999999
	bestRDNP = -1.0
	acum_config =  ''
	
	increase_th = 0.9
	decrease_th = 1.1

	params = getConfigs()
	increase_comp = False
	stable = False
	decrease_comp = True
	runComp = False
	config = ''
	while (not runComp):

		if increase_comp:
			curr_param = getWorstRDNP(params)
			if curr_param in config:
				config = removeParam(config, curr_param, params)
			else:
				config = scaleUp(config, curr_param, params)

		elif decrease_comp:
			curr_param = getBestRDNP(params)
			if curr_param not in config:
				config = addParam(config, curr_param, params)
			elif notFullyTrained(params):
				curr_param = getWorstRDNP(params)
				[config, curr_param] = switchParam(config, curr_param, params)
			else:
				config = scaleDown(config, curr_param, params)
			
		print config

		if notFullyTrained(params) and not stable:
			runComp = run(App, config, 4)
		else:
			runComp = run(App, config, testingPeriod)


		[comp, RDNP] = parseOutput()
		updateParamTable(params, curr_param, comp, RDNP)
		
		print ('%.2f' % (comp/targetComputation))
		
		increase_comp = False
		decrease_comp = False

		if (comp/targetComputation) <= increase_th:
			increase_comp = True
		elif (comp/targetComputation) >= decrease_th:
			decrease_comp = True
		stable = not(increase_comp) and not(decrease_comp)

	return




initComputation = initialPhase(App, initialPeriod)
targetComputation = initComputation*0.6

testingPhase(App,testingPeriod, targetComputation, initComputation)

wrapUp()

