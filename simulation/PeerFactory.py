'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''

from simulation.SimElement import SimElement
from simulation.Simulator import Simulator
from simulation.SSimulator import SSimulator
from utils.Log import Log
from nodes.Peer import Peer
from nodes.Peer_C1 import Peer_C1
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
            for i in range ( 0, 20 ):
                self.addPeer()                

            for i in range ( 0, 20):
                self.addPeer_C1()

        else:
            if SSimulator().tick > (SSimulator().SIM_END - 100) :
                return

            if self.spawnPeer() == True:
                self.addPeer()

            if self.spawnPeer_C1() == True:
                self.addPeer_C1()

    def addPeer(self):
        uploadRate = random.randint( 1024*5, 1024*10 )
        downloadRate = random.randint ( 1024*10, 1024*20 )
        p = Peer( Torrent( 1024*1024*1, self.__tracker ) , uploadRate, downloadRate ) #Create new peer
        Log.w(Log.INFO, "New Peer {0} Up/Down [{1}/{2}]".format(p.pid, uploadRate, downloadRate) )
        self.__tracker.addPeer(p)


    def addPeer_C1(self):
        uploadRate = random.randint( 1024*5, 1024*10 )
        downloadRate = random.randint ( 1024*10, 1024*20 )
        p = Peer_C1( Torrent( 1024*1024*1, self.__tracker ) , uploadRate, downloadRate ) #Create new peer
        Log.w(Log.INFO, "New Peer_C1 {0} Up/Down [{1}/{2}]".format(p.pid, uploadRate, downloadRate) )
        self.__tracker.addPeer(p)
 
    def spawnPeer(self):
        r = random.random()
        if r < 0.1:
            return True
        else:
            return False
    
    def spawnPeer_C1(self):
        r = random.random()
        if r < 0.1:
            return True
        else:
            return False
