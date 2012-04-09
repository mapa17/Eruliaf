'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''

from nodes.Node import Node
import random


class Tracker(Node):

    CpeerSampleSize = 30

    def __init__(self):
        Node.__init__(self)
        self._peers = []
        #self.__id = SSimulator().getNewPeerId()

    def __str__(self, *args, **kwargs):
        return "Tracker"
        
    def addPeer(self, peer):
        self._peers.append(peer)
   
    def remPeer(self, peer):
        self._peers.remove(peer)

    #Returns a set of Peers
    def getPeerList(self):
        
        sampleSize = self.CpeerSampleSize
        
        if(sampleSize > len(self._peers) ):
            sampleSize = len(self._peers)
            
        pL = random.sample(self._peers, sampleSize)
        
        return pL
