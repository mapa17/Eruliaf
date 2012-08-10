'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es

    Copyright (C) 2012  Pasieka Manuel , mapa17@posgrado.upv.es

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
        if(peer not in self._peers):
            self._peers.append(peer)
        else:
            print("Error! Something tried to add the same peer twice!")
   
    def remPeer(self, peer):
        self._peers.remove(peer)

    def connect(self, peer):
        self.addPeer(peer)

    #Returns a set of Peers
    def getPeerList(self):
        
        sampleSize = self.CpeerSampleSize
        
        if(sampleSize > len(self._peers) ):
            sampleSize = len(self._peers)
            
        pL = random.sample(self._peers, sampleSize)
        
        return pL
