'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''
from simulation.SimElement import SimElement
from simulation.SSimulator import SSimulator

class Node(SimElement):

    __id = -1 

    def __init__(self):
        SimElement.__init__(self)
        self.__id = SSimulator().getNewNodeId()
        
    def __str__(self, *args, **kwargs):
        return "Node (0)".format(self.__id)
    
    def getNodeId(self):
        return self.__id
        