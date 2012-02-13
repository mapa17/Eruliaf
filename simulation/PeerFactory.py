'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''

from simulation.SimElement import SimElement
from simulation.Simulator import Simulator
from simulation.SSimulator import SSimulator
from utils.Log import Log
from nodes.Peer import Peer
from utils.Torrent import Torrent
import random

class PeerFactory(SimElement):

    def __init__(self, tracker):
       super().__init__()
       self.__tracker = tracker
       self.registerSimFunction(Simulator.ST_INIT, self.spawnPeers )

    def spawnPeers(self):
        if( SSimulator().tick == 0 ):
            Log.w(Log.DEBUG, "Creating new peers ...")
            for i in range ( 0, 100 ):
                uploadRate = random.randint( 1024*5, 1024*10 )
                downloadRate = random.randint ( 1024*10, 1024*20 )
                p = Peer( Torrent( 1024*1024*1, self.__tracker ) , uploadRate, downloadRate ) #Create new peer
                Log.w(Log.DEBUG, "New Peer {0}".format(p.pid) )
                self.__tracker.addPeer(p)
                
