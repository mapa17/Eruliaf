'''
Created on Feb 16, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''

from simulation.SSimulator import SSimulator
from simulation.Simulator import Simulator
from simulation.SimElement import SimElement
from nodes.Peer import Peer
from nodes.Peer_C1 import Peer_C1

class Observer(SimElement):

    def __init__(self, tracker):
        super().__init__()
        
        self._peers = []
        self._tracker = tracker

        statsPath = "./statistics/"
        self.dt_peer =  statsPath + "dt_peer.csv"
        self.dt_peer_c1 =  statsPath + "dt_peer_c1.csv"
        
        #Stats
        self._downloadTime = False
        self._completedPeers = False
        self._numberOfPeers = False
        self._bandwidthDistribution = False
        self._updownBandwidthRation = False

        self._readConfig()
        self._createOutputFiles()

        self.registerSimFunction(Simulator.ST_STATISTICS, self.logic )
        self.registerSimFunction(Simulator.ST_SIMULATION_END, self._endSimulation )

    def logic(self):
        for p in self._tracker._peers: 
            if( self._downloadTime ):
                self._statDownloadTime(p)

    def _readConfig(self):
        self._downloadTime = True
        self._completedPeers = False
        self._numberOfPeers = False
        self._bandwidthDistribution = False
        self._updownBandwidthRation = False

    def _statDownloadTime(self, peer):
        if( isinstance(peer, Peer) ):
            fd = self._fd_DownloadTime_Peer

        if( isinstance(peer, Peer_C1) ):
            fd = self._fd_DownloadTime_Peer_C1
        
        #Check if this peer finished its download this round if so, write it to file
        if peer._torrent._finishTick == SSimulator().tick :
            fd.write( "{0};{1};{2}\n".format(peer.pid, peer._birth, peer._torrent._finishTick) )
        

    def _endSimulation(self):
        self._closeOutputFiles()

    def _createOutputFiles(self):
        if( self._downloadTime == True ):
            formatDesc = "# Log format <Peer id> <Tick of Download started/birth> <Tick when the download was finished>\n"
            self._fd_DownloadTime_Peer = open( self.dt_peer, "w" )
            self._fd_DownloadTime_Peer.write(formatDesc)
            self._fd_DownloadTime_Peer_C1 = open( self.dt_peer_c1, "w" )
            self._fd_DownloadTime_Peer_C1.write(formatDesc)

    def _closeOutputFiles(self):
        if( self._downloadTime == True ):
            self._fd_DownloadTime_Peer.close()
            self._fd_DownloadTime_Peer_C1.close()

