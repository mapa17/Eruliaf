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
from simulation.SConfig import SConfig

class PeerFactory(SimElement):

    def __init__(self, tracker):
        super().__init__()
        self.__tracker = tracker
        self.registerSimFunction(Simulator.ST_INIT, self.spawnPeers )
        
        random.seed( int(SConfig().value("randSeed"))  )
        self._peerSpawnRate = float( SConfig().value("SpwanRate" , "Peer") )
        self._peerC1SpawnRate = float( SConfig().value("SpwanRate" , "PeerC1") )
        self._simEnd = int( SConfig().value("SimEnd") )
        
        self._maxSleep = int( SConfig().value("MaxSleep", "Peer") )
        self._C1maxSleep = int( SConfig().value("MaxSleep", "PeerC1") )
        
        self.uMax = int( SConfig().value("UploadRateMax" , "Peer") )
        self.uMin = int( SConfig().value("UploadRateMin" , "Peer") )
        self.dMax = int( SConfig().value("DownloadRateMax" , "Peer") )
        self.dMin = int( SConfig().value("DownloadRateMin" , "Peer") )
        
        self.C1uMax = int( SConfig().value("UploadRateMax" , "PeerC1") )
        self.C1uMin = int( SConfig().value("UploadRateMin" , "PeerC1") )
        self.C1dMax = int( SConfig().value("DownloadRateMax" , "PeerC1") )
        self.C1dMin = int( SConfig().value("DownloadRateMin" , "PeerC1") )

    def spawnPeers(self):
        if( SSimulator().tick == 0 ):
            Log.w(Log.DEBUG, "Creating new peers ...")
            for i in range ( 0, int(SConfig().value("nInitialPeers" , "Peer")) ):
                self.addPeer()                

            for i in range ( 0, int( SConfig().value("nInitialPeers" , "PeerC1")) ):
                self.addPeer_C1()

        else:
            if self.spawnPeer() == True:
                self.addPeer()

            if self.spawnPeer_C1() == True:
                self.addPeer_C1()

    def addPeer(self):
        uploadRate = random.randint( self.uMin, self.uMax )
        downloadRate = random.randint ( self.dMin, self.dMax )
        sleep = random.randint(0, self._maxSleep)
        p = Peer( Torrent( self.__tracker ) , uploadRate, downloadRate, sleep ) #Create new peer
        Log.w(Log.INFO, "New Peer {} Up/Down [{}/{}] Sleep {}".format(p.pid, uploadRate, downloadRate, sleep) )
        self.__tracker.addPeer(p)


    def addPeer_C1(self):
        uploadRate = random.randint( self.C1uMin, self.C1uMax )
        downloadRate = random.randint ( self.C1dMin, self.C1dMax )
        sleep = random.randint(0, self._C1maxSleep)
        p = Peer_C1( Torrent( self.__tracker ) , uploadRate, downloadRate, sleep ) #Create new peer
        Log.w(Log.INFO, "New Peer_C1 {} Up/Down [{}/{}] Sleep {}".format(p.pid, uploadRate, downloadRate, sleep) )
        self.__tracker.addPeer(p)
 
    def spawnPeer(self):
        r = random.random()
        if r < self._peerSpawnRate:
            return True
        else:
            return False
    
    def spawnPeer_C1(self):
        r = random.random()
        if r < self._peerC1SpawnRate:
            return True
        else:
            return False
