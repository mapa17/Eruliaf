'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''
from nodes.Node import Node
import random


class Tracker(Node):

    CpeerSampleSize = 10

    def __init__(self):
        Node.__init__(self)
        self.__peers = []
        #self.__id = SSimulator().getNewPeerId()

    def __str__(self, *args, **kwargs):
        return "Tracker"
        
    def addPeer(self, peer):
        self.__peers.append(peer)
        
    def getPeerList(self):
        
        sampleSize = self.CpeerSampleSize
        
        if(sampleSize > len(self.__peers) ):
            sampleSize = len(self.__peers)
            
        pL = random.sample(self.__peers, sampleSize)
        
        return pL