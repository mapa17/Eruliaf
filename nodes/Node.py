'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''
from simulation.SimElement import SimElement
from simulation.SSimulator import SSimulator

class Node(SimElement):

    nid = -1 

    def __init__(self):
        super().__init__()
        self.nid = SSimulator().getNewNodeId()
        
    def __str__(self, *args, **kwargs):
        return "Node (0)".format(self.nid)
    
    def getNodeId(self):
        return self.nid
        