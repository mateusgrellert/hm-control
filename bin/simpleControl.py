from HM_setup import *
import os

def initialPhase(App, configurationMap, initialPeriod):
	print '## Starting Phase ###'

	run(App, ' --BipredSearchRange=8 --SearchRange=80 ', initialPeriod)
	[initComputation, RDNP] = parseOutput(start=True)
	configurationMap[' --BipredSearchRange=8 --SearchRange=80 '] = [initComputation, RDNP]

	return initComputation

def testingPhase(App, configurationMap, testingPeriod, targetComputation, currComp):
	print '## Testing Phase ###'
	bestComputation = 999999
	bestRDNP = -1.0

	safe_zone = 0.2
	combine_th = safe_zone
	split_th = -safe_zone
	stable_th = 0.05

	stable_flag = False
	combine_flag = False
	split_flag = False
	train_flag = False
	scaleUp_flag = False
	scaleDown_flag = False
	run_ended = False
	parameters = getParameters()
	idx = 0

	config = ' '
	while not run_ended:

		if combine_flag:
			while parameters[idx] in currParams:
				idx += 1
			
			currParams = parameters[idx % len(parameters)]
			config = combineConfigs(currParam, config)


		elif scaleUp_flag:
			config = upScaleParameters(config)

		elif scaleDown_flag:
			config = downScaleParameters(config)

		elif split_flag:
			config = splitConfig(config)

		while (config in configurationMap.keys()):
			error = (configurationMap[config][0]/targetComputation - 1.0)
			if error <= split_th:
				splitConfig
		
		print config

		run_ended = run(App, config, testingPeriod)
		configurationMap[config] = parseOutput()
			
		testComputation = configurationMap[config][0]
		RDNP = configurationMap[config][1]

		rate = testComputation/currComp
		if compRateTable[p
		error = (testComputation/targetComputation - 1.0)
		delta = (testComputation - targetComputation)
		print ('%.2f\t%.2f\t%.2f' % (testComputation, targetComputation, error))

		combine_flag = (error >= combine_th)
		split_flag = (error <= split_th)
		stable_flag = abs(error) <= stable_th
		scaleDown_flag = not(combine_flag or split_flag or stable_flag) and (error > 0)				
		scaleUp_flag = not(combine_flag or split_flag or stable_flag) and (error <= 0)


		"""if scaleDown_flag or scaleUp_flag:
			if RDNP < bestRDNP:
				config = bestConfig
			else:
				bestConfig = config
				bestRDNP = RDNP"""

	print '## Run Ended ###'



initComputation = initialPhase(App, configurationMap, initialPeriod)

targetComputation = initComputation*0.5

testingPhase(App, configurationMap,testingPeriod, targetComputation, initComputation)

wrapUp()

