'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''
from simulation.SSimulator import SSimulator

class SimElement(object):

    def __init__(self):
        SSimulator().addSimulationElement(self)
    
    def __str__(self, *args, **kwargs):
        return "Simulation Element"
    
    def nextTick(self, tick, stage):
        print("{2} running tick [{0} : {1}]".format(tick, stage, self ) )
    