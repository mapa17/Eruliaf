'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''
from nodes.Node import Node
from simulation.SSimulator import SSimulator

class Peer(Node):

    __id = -1

    def __init__(self):
        Node.__init__(self)
        self.__id = SSimulator().getNewPeerId()
    

    def __str__(self, *args, **kwargs):
        return "Peer (0)".format(self.__id)
        