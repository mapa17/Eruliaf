'''
Created on Feb 2, 2012

@author: dd
'''
from nodes.Node import Node

class Tracker(Node):

    def __init__(self):
        Node.__init__(self)
        #self.__id = SSimulator().getNewPeerId()

    def __str__(self, *args, **kwargs):
        return "Tracker"
        