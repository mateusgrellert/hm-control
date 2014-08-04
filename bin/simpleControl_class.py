class SimpleControl(self):
	
	def __init__(self):
		self.numSteps = 50

	def runApp(self):
		self.initialPhase (App, initConfig, trainingPeriod)
		initComputation = self.getComputation()
		targetComputation = initComputation*0.5
		print '\tInital Time: ', initComputation, '\t Target: ', targetComputation
		bestConfig = initConfig

	def initialPhase(App, initConfig, trainingPeriod):
		print '## Starting Phase ###'
		self.initialSet = []

		run(App, initConfig, trainingPeriod)
		output = parseOutput(start=True)
		initialSet.append(output)


	def testingPhase(App, configs,testingPeriod, targetComputation):
		print '## Testing Phase ###'
		bestComputation = 999999
		for config in configs:
			testingSet = []

			run(App, config, testingPeriod)
			output = parseOutput()
			testingSet.append(output)
				
			testComputation = getComputation(testingSet)
			print '\t ',config.split('--IntraPeriod=-1')[-1], ': ',testComputation
			if testComputation <= targetComputation:
				print '\n\tBest Configuration: ', config.split('--IntraPeriod=-1')[-1], '\n\t\tTime: ', testComputation, '\t Target: ',targetComputation
				return config
			elif testComputation < bestComputation:
				bestConfig = config
				bestComputation = testComputation
	
		print '\n\tBest Configuration: ', bestConfig.split('--IntraPeriod=-1')[-1], '\n\t\tTime: ', bestComputation, '\t Target: ',targetComputation

		return bestConfig

	def runningPhase(App, configs,runningPeriod, targetComputation):
		print '## Running Phase ###'
		global stepsTaken

		while(stepsTaken < numSteps):
			print stepsTaken, numSteps
			runningSet = []

			run(App, bestConfig, runningPeriod)

			output = parseOutput()
			runningSet.append(output)

			runComputation = getComputation(runningSet)
			
			print '\tRun Computation: ', runComputation

			if runComputation > targetComputation:
				return False

		return True

	def getComputation(outputSet):
		acum = 0.0
		for output in outputSet:
			acum += output
		return acum/len(outputSet)
