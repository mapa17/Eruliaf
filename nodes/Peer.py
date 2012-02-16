'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''

from nodes.Node import Node
from simulation.SSimulator import SSimulator
from nodes.Connection import Connection
import random
from simulation.Simulator import Simulator
from utils.Log import Log

class Peer(Node):

    pid = -1
    TFTPeriod = 10    # number of ticks a TFT slot is active
    OUPeriod = 30     # number of ticks a UO slot is active
    __minPieceInterestSize =  20

    NO_SLOT = -1
    TFT_SLOT = 1
    OU_SLOT = 2

    def __init__(self, torrent, maxUploadRate, maxDownloadRate):
        super().__init__()
        self.pid = SSimulator().getNewPeerId()
        self._torrent = torrent
        self._maxTFTSlots = 2
        self._maxOUSlots = 1
        self._nTFTSlots = 0
        self._nOUSlots = 0
        self._minPeerListSize = 10 #TODO: change this to 30
        self._maxDownloadRate = maxDownloadRate
        self._maxUploadRate = maxUploadRate
        self._activeDownloadBandwidthUsage = 0

        self.piecesQueue = set() #Set of pieces to download next
        
        self._peersConn = {} #Empty dictionary
       
        self._isSeeder = False 

        self.registerSimFunction(Simulator.ST_UPDATE_LOCAL, self.updateLocalConnectionState )
        self.registerSimFunction(Simulator.ST_UPDATE_GLOBAL, self.updateGlobalConnectionState )
        self.registerSimFunction(Simulator.ST_LOGIC, self.peerLogic )
       
        #self.__wasUnchocked = False
        #Start right away
        #self.__TFTSlotAge = self.TFTPeriod
        #self.__OUSlotAge = self.OUPeriod
    
    def __del__(self):
        Log.pLD("Peer is beeing destroyed")

    def __str__(self, *args, **kwargs):
        return "Peer [pid {0}, nid {1} ]".format(self.pid, self.nid)
    
    #Getting list of peer from tracker and add unknown ones to our own peer list 
    def getNewPeerList(self):
        #print("Getting a new peer list from the tracker ...")
        newPeers = self._torrent.tracker.getPeerList()

        #Filter unwanted peers , for example itself
        def f(x): return ( x.pid != self.pid )
        newPeers = filter( f, newPeers )

        for i in newPeers :
            if (i.pid in self._peersConn) == False:
                newConnection = Connection(self, i)
                self._peersConn[i.pid] = ( 0, i.pid, newConnection, -1 , self.NO_SLOT )
                newConnection.setUploadLimit( self._calculateUploadRate(newConnection) )
                #newConnection.setDownloadLimit( self._calculateDownloadRate(newConnection) )
                newConnection.connect()
                Log.pLD(self, "adding Peer [{0}]".format(i.pid))
    
    #Is called from an foreign peer to connect to this peer
    def connectToPeer(self, peer):
        #logging.log(Simulator.DEBUG, "[{0}] External peer is connecting! [{1}]".format(self.pid, peer.pid))
        Log.pLD(self, "External peer is connecting! [{0}]".format(peer.pid) )
        newConnection = None
            
        #If we already now this peer, return current connection
        if peer.pid in self._peersConn :
            newConnection = self._peersConn[peer.pid][2]
        else:
            Log.pLD(self, "adding Peer [{0}]".format(peer.pid)) 
            newConnection = Connection(self, peer)
            self._peersConn[peer.pid] = ( 0, peer.pid, newConnection, -1 , self.NO_SLOT)
            newConnection.setUploadLimit( self._calculateUploadRate(newConnection) )
            #newConnection.setDownloadLimit( self._calculateDownloadRate(newConnection) )
            self._peersConn[peer.pid][2].connect()
        
        #Return the connection reference
        return newConnection
            

    def updateLocalConnectionState(self):   
        self._activeDownloadBandwidthUsage = 0

        if self._torrent.isFinished() == True :
            #So check if we want to leave or stay as a seeder
            if( self._leaveTorrent() == True ):
                self._torrent.tracker.remPeer(self)
                self._disconnectConnections()
                self.removeSimElement()
                Log.pLI(self, "Leaving torrent ...")
        else:
            if( (len(self.piecesQueue) < self.__minPieceInterestSize ) ):
                Log.pLD(self, "Getting new piece list for downloading ..." )
                self.piecesQueue = self.pieceSelection(self.__minPieceInterestSize*3) #Simulates the queuing of piece requests to other peers
        
        finishedPieces = self._torrent.getFinishedPieces()
        for i in self._peersConn.values() :
            i[2].updateLocalState(finishedPieces)            

    
    def updateGlobalConnectionState(self):
        
        #Have to do this twice, because updateGlobalState() will remove disconnected peers from the peerConn list
        copy = self._peersConn.copy()
        for i in copy.values() :
            i[2].updateGlobalState()
        
        for (k, v) in self._peersConn.items():
            #Some connection may have been chocked, if so free the slot and force a new OU or TFT algorithm call
            if v[2].chocking == True:
                self._peersConn[k] = ( v[2].getDownloadRate(), v[1], v[2], -1 , v[4]) #Dont modify conn state (v[4]) this will be doen in _doChocking()
            else:
                self._peersConn[k] = ( v[2].getDownloadRate(), v[1], v[2], v[3] , v[4]) #Update the UploadRate field in the tuple

    def peerLogic(self):

        if(len(self._peersConn) < self._minPeerListSize):
            self.getNewPeerList()
 
        self._doChocking()

        tftChoosen = list()
        ouChoosen = list()

        if(self._torrent.isFinished() == False):
            #Leecher
                        
            unusedSlots = 0
           
            if( self._nTFTSlots < self._maxTFTSlots ):

                nSlots = self._maxTFTSlots + self._maxOUSlots - self._nOUSlots + self._nTFTSlots
                if( nSlots + self._nTFTSlots > self._maxTFTSlots ):
                    nSlots = self._maxTFTSlots - self._nTFTSlots
                #nSlots = self._maxTFTSlots - self._nTFTSlots
                #if(nSlots + self._nOUSlots > self._maxTFTSlots + self._maxOUSlots ):
                #    nSlots = nSlots + self._nTFTSlots + self._nOUSlots - self._maxTFTSlots
                
                if(nSlots>0):
                    tftChoosen = self.runTFT(nSlots)
                    self._TFTUnchock(tftChoosen)
                    unusedSlots = self._maxTFTSlots - self._nTFTSlots - len(tftChoosen)
                else:
                    pass
            
            if( (unusedSlots>0) or (self._nOUSlots < self._maxOUSlots) ) :
                nSlots = self._maxTFTSlots+self._maxOUSlots - self._nTFTSlots - self._nOUSlots
                if( nSlots < 0):
                    pass
                ouChoosen = self.runOU(nSlots)
                self._OUUnchock(ouChoosen)
            
        else:
            #Seeder Part
            nSlots = self._maxOUSlots + self._maxTFTSlots - self._nOUSlots - self._nTFTSlots
            if( nSlots > 0):
                ouChoosen = self.runOU(nSlots)
                self._OUUnchock(ouChoosen)
        
        #Print statistics about the node
        self._printStats()    

    #Is called by the connection passed as argument to tell the peer about a disconected peer
    def peerDisconnect(self, conn):

        copy = self._peersConn.copy()
        for (k, v) in copy.items():
            if v[2] ==  conn:
                if v[4] == self.OU_SLOT :
                    self._nOUSlots -= 1
                if v[4] == self.TFT_SLOT :
                    self._nTFTSlots -=1

                del self._peersConn[k]
                break #The connection can only have existed once
                
        #Log.pLD(self, "Peer {0} disconnected ... ".format(conn.) )

    def requestDownloadBandwidth(self, bandwidth):
        if( self._activeDownloadBandwidthUsage + bandwidth < self._maxDownloadRate ):
            self._activeDownloadBandwidthUsage += bandwidth
        else:
            bandwidth = self._maxDownloadRate - self._activeDownloadBandwidthUsage
            self._activeDownloadBandwidthUsage = self._maxDownloadRate
        
        return bandwidth

    def _calculateUploadRate(self, connection):
        return self._maxUploadRate / ( self._maxTFTSlots + self._maxOUSlots ) 

    #def _calculateDownloadRate(self, connection):
    #    return self._maxDownloadRate / ( self._maxTFTSlots + self._maxOUSlots ) 

    def _leaveTorrent(self):

        if self._isSeeder:
            return False

        i = random.random() * 100
        if ( i < 10 ) :
            return True
        else:
            return False

    def _disconnectConnections(self):
        for i in self._peersConn.values():
            i[2].disconnect()

    def _doChocking(self):
        t = SSimulator().tick

        for i in self._peersConn.values() :
            if i[3] <= t :
                #Only call chock on open connections
                if i[4] == self.OU_SLOT :
                    self._nOUSlots -= 1
                    i[2].chock()
                if i[4] == self.TFT_SLOT :
                    self._nTFTSlots -=1
                    i[2].chock()

                self._peersConn[i[1]] = ( i[0],i[1],i[2],i[3], self.NO_SLOT )

    def _OUUnchock(self, ouChoosen):

        #Unchock OU
        for i in ouChoosen:
            self._peersConn[i[1]] = i
            self._nOUSlots += 1
            self._peersConn[i[1]][2].unchock()
    
    def _TFTUnchock(self, tftChoosen):

        #Unchock TFT
        for i in tftChoosen:
            self._peersConn[i[1]] = i
            self._nTFTSlots += 1
            self._peersConn[i[1]][2].unchock()
            
    def _printStats(self):
       
        '''
        #Print list of unchocked peers
        def f(x): return ( x[2].chocking==False )
        candidates = filter( f, self._peersConn )
        reduced = []
        for i in candidates:
            reduced.append(i[1])
        Log.pLD(self, "Unchocked peers {0}".format(reduced) )
        '''

        #Print OU Candidates
        #Log.pLD(self, "OU Candidates {0}".format( self.getOUCandidates() ) )

        #Print PeerList
        t = []
        for i in self._peersConn.values():
            t.append( "( {0}@{1}/{2} {3}|{4}|{5}|{6} , {7}|{8})".format(i[1], \
                            i[2].getUploadRate(), \
                            i[2].getDownloadRate(),  \
                            1 if i[2].chocking == True else 0, \
                            1 if i[2].interested == True else 0, \
                            1 if i[2].peerIsChocking() == True else 0, \
                            1 if i[2].peerIsInterested() == True else 0, \
                            i[3], \
                            "N" if i[4] == self.NO_SLOT else "T" if i[4] ==  self.TFT_SLOT else "O", \
                            ) )

        Log.pLI(self, "DL {0}/{1} i{2} TFT {3}, OU {4} , PeerList {5}".format(self._torrent.getNumberOfFinishedPieces(), \
            self._torrent.getNumberOfPieces(), \
            len(self.piecesQueue), \
            self._nTFTSlots, self._nOUSlots, t) )
                        
    '''
        The Tit-for-tat algorithm ranks peers on their upload speed provided to this node.
        Take the <nSlots> highest ranked peers and execute the TFT algorithm on them 
    '''
    def runTFT(self, nSlots):
        Log.pLD(self, " Executing TFT Algorithm for {0}".format(nSlots) )
        #self._peersConn.sort() #Peer list in the form ( <UploadRate>, <PeerID>, <Connection> ) , sort will on the first field and on collision continue with the others
        
        t = SSimulator().tick
        chosen = list()
        candidates = self.getTFTCandidates()
        
        if(len(candidates) > 0):
            candidates.sort(reverse=True) #Sort candidates based on their uploadRate, (highest uploadRate first)
            if(nSlots > len(candidates)):
                nSlots = len(candidates)

            while(nSlots > 0):
                p = candidates.pop(0)
                #Set Conneciton TTL 
                p = ( p[0], p[1], p[2], t + self.TFTPeriod, self.TFT_SLOT )
                chosen.append( p )
                nSlots-=1
           
        if(nSlots > 0):
            Log.pLW(self, " not enough peers to fill all TFT slots ... {0} unfilled.".format(nSlots) )
        
        return chosen
        
    def runOU(self, nSlots):
        Log.pLD(self, "Executing OU Algorithm for {0}".format(nSlots) )
        #print("[{0}] peers [ {1} ]".format(self.pid, self._peersConn))
       
        t = SSimulator().tick

        #Skip if nothing to do
        if(nSlots == 0):
            return set()
       
        if(nSlots < 0):
            Log.pLE(self, "Error in calculating the number of OU slots to schedule. Will skip OU at this step!")
            return set()
       
        candidates = self.getOUCandidates()

        if( len(candidates) < nSlots ):
            Log.pLD(self, " not enough peers to populate all OU slots ... {0} unfilled.".format(nSlots - len(candidates)) )
            nSlots = len(candidates)      
        
        chosen = list( random.sample(candidates, nSlots) )

        #Set Connection TTL
        for (idx, v) in enumerate(chosen):
            chosen[idx] = ( v[0], v[1], v[2], t + self.OUPeriod, self.OU_SLOT)

        return chosen

    def finishedDownloadingPiece(self, conn, piece):
        self._torrent.finishedPiece( piece )
        if piece in self.piecesQueue:
            self.piecesQueue.remove(piece)

    def downloadingPiece(self, conn, piece):
        if piece in self.piecesQueue:
            self.piecesQueue.remove(piece)

    #Implementing Rarest piece first piece selection
    def pieceSelection(self, nPieces):
        if( SSimulator().tick == 590 ):
            pass
        emptyPieces = self._torrent.getEmptyPieces( self._torrent.getNumberOfPieces() )
        pieceHistogram = [ (0,x) for x in range(0, self._torrent.getNumberOfPieces()) ]
        for i in self._peersConn.values():
            #Get a set of finished pieces
            finished = i[2].remoteConnection.finishedPieces & emptyPieces
            for k in finished:
                pieceHistogram[k] = ( pieceHistogram[k][0] + 1, pieceHistogram[k][1])

        #Filter elements that none has
        def f(x): return ( x[0] != 0 )
        pieceHistogram = list( filter(f, pieceHistogram ) )

        #Sort the histogram on the number of counts of finished pieces, least common are at the end
        pieceHistogram.sort()

        if nPieces > len(pieceHistogram):
            nPieces = len(pieceHistogram)
        
        rarestPieces = set()

        while nPieces > 0:
            rarestPieces.add(pieceHistogram.pop(0)[1])
            nPieces -= 1
        
        return rarestPieces

    def getTorrent(self):
        return self._torrent

    #def getUnchockedPeers(self):
    #    def f(x): return ( x[2].chocking == False )
    #    unchocked = list( filter( f, self._peersConn ) )
    #    return unchocked


    #Get a list of peers that we are currently not working with is not ourself  but have interest in us
    def getOUCandidates(self):
        #def f(x): return ( ( x[2].peerIsInterested() == True ) and ( x[3] <= SSimulator().tick ) )
        #candidates = list( filter( f, self._peersConn ) )
        candidates = list()
        for i in self._peersConn.values():
            if(( i[2].peerIsInterested() == True ) and ( i[3] <= SSimulator().tick ) ):
                candidates.append(i)

        return candidates

    #Get a list of peers that are interested in our data and have at least downloaded one slot ( either TFT or OU )
    def getTFTCandidates(self):
        #def f(x): return ( ( x[0] > 0 ) and ( x[2].peerIsInterested() == True) and ( x[3] <= SSimulator().tick ) )
        #candidates = list( filter( f, self._peersConn ) )
        
        candidates = list()
        for i in self._peersConn.values():
            if( ( i[0] > 0 ) and ( i[2].peerIsInterested() == True ) and ( i[3] <= SSimulator().tick ) ):
                candidates.append(i)

        return candidates
 
