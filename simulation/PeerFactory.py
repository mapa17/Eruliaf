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
        self._peerSpawnRate = float( SConfig().value("SpwanRate" , "PeerFactor_Peer") )
        self._peerC1SpawnRate = float( SConfig().value("SpwanRate" , "PeerFactor_PeerC1") )
        self._simEnd = int( SConfig().value("SimEnd") )

    def spawnPeers(self):
        if( SSimulator().tick == 0 ):
            Log.w(Log.DEBUG, "Creating new peers ...")
            for i in range ( 0, int(SConfig().value("nInitialPeers" , "PeerFactor_Peer")) ):
                self.addPeer()                

            for i in range ( 0, int( SConfig().value("nInitialPeers" , "PeerFactor_PeerC1")) ):
                self.addPeer_C1()

        else:
            if SSimulator().tick > ( self._simEnd - 100) :
                return

            if self.spawnPeer() == True:
                self.addPeer()

            if self.spawnPeer_C1() == True:
                self.addPeer_C1()

    def addPeer(self):
        uMax = int( SConfig().value("UploadRateMax" , "PeerFactor_Peer") )
        uMin = int( SConfig().value("UploadRateMin" , "PeerFactor_Peer") )
        dMax = int( SConfig().value("DownloadRateMax" , "PeerFactor_Peer") )
        dMin = int( SConfig().value("DownloadRateMin" , "PeerFactor_Peer") )
         
        uploadRate = random.randint( uMin, uMax )
        downloadRate = random.randint ( dMin, dMax )
        p = Peer( Torrent( int(SConfig().value("TorrentSize" )), self.__tracker ) , uploadRate, downloadRate ) #Create new peer
        Log.w(Log.INFO, "New Peer {0} Up/Down [{1}/{2}]".format(p.pid, uploadRate, downloadRate) )
        self.__tracker.addPeer(p)


    def addPeer_C1(self):
        uMax = int( SConfig().value("UploadRateMax" , "PeerFactor_PeerC1") )
        uMin = int( SConfig().value("UploadRateMin" , "PeerFactor_PeerC1") )
        dMax = int( SConfig().value("DownloadRateMax" , "PeerFactor_PeerC1") )
        dMin = int( SConfig().value("DownloadRateMin" , "PeerFactor_PeerC1") )
         
        uploadRate = random.randint( uMin, uMax )
        downloadRate = random.randint ( dMin, dMax )
        p = Peer_C1( Torrent( int(SConfig().value("TorrentSize" )), self.__tracker ) , uploadRate, downloadRate ) #Create new peer
        Log.w(Log.INFO, "New Peer_C1 {0} Up/Down [{1}/{2}]".format(p.pid, uploadRate, downloadRate) )
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
