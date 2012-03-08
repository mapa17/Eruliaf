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
        self.peerCntPath =  statsPath + "peerCnt.csv"
        self.peerCntPathC1 =  statsPath + "peerCntC1.csv"
        self.connStats = statsPath + "Conn.csv"
        
        #Stats
        self._downloadTime = False
        self._peerCnt = False
        self._conn = False
        self._bandwidthDistribution = False
        self._updownBandwidthRation = False

        self._readConfig()
        self._createOutputFiles()

        self.registerSimFunction(Simulator.ST_STATISTICS, self.logic )
        self.registerSimFunction(Simulator.ST_SIMULATION_END, self._endSimulation )

    def logic(self):
        #Run for every peer
        for p in self._tracker._peers: 
            if( self._downloadTime ):
                self._statDownloadTime(p)
        
        #Run once per tick
        if( self._peerCnt == True ):
            self._statPeerCnt()
        
        if( self._conn == True ):
            self._statConn()

    def _readConfig(self):
        self._downloadTime = True
        self._peerCnt = True
        self._conn = True
        self._bandwidthDistribution = False
        self._updownBandwidthRation = False

    #Log the number of total TFT/OU Connections for each peer class
    def _statConn(self):
        peerTFT = [0,0]
        peerTFTMax = [0,0]
        peerOU = [0,0]
        peerOUMax = [0,0]
        peerCnt = [0,0]
        
        #Count number of peers and number of completed peers
        for p in self._tracker._peers:
            if( isinstance(p, Peer) ):
                pos = 0
            
            if( isinstance(p, Peer_C1) ):
                pos = 1
            
            peerCnt[pos] += 1
            peerTFT[pos] += p._nTFTSlots
            peerOU[pos] += p._nOUSlots
            peerTFTMax[pos] += p._maxTFTSlots
            peerOUMax[pos] += p._maxOUSlots

        # <Tick> <peer Type> <Total # of max TFT Slots> <Total # of max OU Slots> <Total # of used TFT Slots> <Total # of used OU Slots> <# of peers>\n"

        #Write Stats to file
        fd = self._fd_conn
        fd.write("{0};{1};{2};{3};{4};{5};{6}\n".format(self.t, "Peer", peerTFTMax[0], peerOUMax[0], peerTFT[0], peerOU[0], peerCnt[0]) )
        fd.write("{0};{1};{2};{3};{4};{5};{6}\n".format(self.t, "Peer_C1", peerTFTMax[1], peerOUMax[1], peerTFT[1], peerOU[1], peerCnt[1]) )
        

    #Log the download time for each completed peer
    def _statDownloadTime(self, peer):
        
        self.t = SSimulator().tick
        
        if( isinstance(peer, Peer) ):
            fd = self._fd_DownloadTime_Peer

        if( isinstance(peer, Peer_C1) ):
            fd = self._fd_DownloadTime_Peer_C1
        
        #Check if this peer finished its download this round if so, write it to file
        if peer._torrent._finishTick == SSimulator().tick :
            fd.write( "{0};{1};{2}\n".format(peer.pid, peer._birth, peer._torrent._finishTick) )
    
    #Log the number of active and completed peers every tick
    def _statPeerCnt(self):
        
        peerCnt = 0
        peerCmpltCnt = 0
        peerCntC1 = 0
        peerCmpltCntC1 = 0
        
        #Count number of peers and number of completed peers
        for p in self._tracker._peers:
            if( p.__class__.__name__ == "Peer" ):
                peerCnt += 1
                if( p._torrent.isFinished() ):
                    peerCmpltCnt += 1

            if( p.__class__.__name__ == "Peer_C1" ):
                peerCntC1 += 1
                if( p._torrent.isFinished() ):
                    peerCmpltCntC1 += 1

        #Write Stats to file
        fd = self._fd_PeerCnt
        fd.write("{0};{1};{2}\n".format(self.t, peerCnt, peerCmpltCnt) )
        
        fd = self._fd_PeerCntC1
        fd.write("{0};{1};{2}\n".format(self.t, peerCntC1, peerCmpltCntC1) )

    def _endSimulation(self):
        self._closeOutputFiles()

    def _createOutputFiles(self):
        if( self._downloadTime == True ):
            formatDesc = "# Log format <Peer id> <Tick of Download started/birth> <Tick when the download was finished>\n"
            self._fd_DownloadTime_Peer = open( self.dt_peer, "w" )
            self._fd_DownloadTime_Peer.write(formatDesc)
            self._fd_DownloadTime_Peer_C1 = open( self.dt_peer_c1, "w" )
            self._fd_DownloadTime_Peer_C1.write(formatDesc)

        if( self._peerCnt == True ):
            formatDesc = "# Log format <Tick> <# of peers> <# of finished peers>\n"
            self._fd_PeerCnt = open( self.peerCntPath, "w" )
            self._fd_PeerCnt.write(formatDesc)
            self._fd_PeerCntC1 = open( self.peerCntPathC1, "w" )
            self._fd_PeerCntC1.write(formatDesc)
            
        if( self._conn == True):
            formatDesc = "# Log format <Tick> <peer Type> <Total # of max TFT Slots> <Total # of max OU Slots> <Total # of used TFT Slots> <Total # of used OU Slots> <# of peers>\n"
            self._fd_conn = open( self.connStats, "w" )
            self._fd_conn.write(formatDesc)

    def _closeOutputFiles(self):
        if( self._downloadTime == True ):
            self._fd_DownloadTime_Peer.close()
            self._fd_DownloadTime_Peer_C1.close()

        if( self._peerCnt == True ):
            self._fd_PeerCnt.close()
            self._fd_PeerCntC1.close()
            
        if( self._conn == True ):
            self._fd_conn.close()
