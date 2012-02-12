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
        self._peersConn = []
        #self.__id = SSimulator().getNewPeerId()

    def __str__(self, *args, **kwargs):
        return "Tracker"
        
    def addPeer(self, peer):
        self._peersConn.append(peer)
   
    def remPeer(self, peer):
        self._peersConn.remove(peer)

    #Returns a set of Peers
    def getPeerList(self):
        
        sampleSize = self.CpeerSampleSize
        
        if(sampleSize > len(self._peersConn) ):
            sampleSize = len(self._peersConn)
            
        pL = random.sample(self._peersConn, sampleSize)
        
        return pL
