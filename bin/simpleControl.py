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
	old_config = ''

	while (not runComp):
		best_params = getBestRDNP(params)
		worst_params = getWorstRDNP(params)
		idx = 0

		while increase_comp:
			increase_comp = False
			curr_param = worst_params[idx]

			if curr_param in old_config:
				config = removeParam(old_config, curr_param, params)
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
		old_config = config

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

