from App_Runner import *
from sys import argv

runner = App_Runner(argv[1], argv[2], argv[3], False)
#runner.cleanUp()


#runner.sensitivityAnalysis(argv[4],'single')
runner.printOutput()
#runner.controlTarget(argv[4])
