'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''
from simulation.SSimulator import SSimulator

class SimElement(object):

    def __init__(self):
        SSimulator().addSimulationElement(self)
        self.__simFunctions = []

    def __str__(self, *args, **kwargs):
        return "Simulation Element"
    
    def nextTick(self, tick, stage):
        #print("{2} running tick [{0} : {1}]".format(tick, stage, self ) )
        
        # self.__simFunctions is holding a list of tuples the kind ( #stage , Function )
        # Iterate through all registered function and execute all for this stage
        
        for i in self.__simFunctions :
            if( (i[0]) == stage ):
                i[1]()

    def registerSimFunction(self, stage, function):
        self.__simFunctions.append( (stage, function) )
    