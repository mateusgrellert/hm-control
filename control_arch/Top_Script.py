from App_Runner import *
from sys import argv

runner = App_Runner(argv[1], argv[2], argv[3])
runner.singleSwitchSensitivityAnalysis(argv[4], 'cumulative')
