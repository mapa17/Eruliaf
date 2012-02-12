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

    __PEER_REDUCED = 1
    __TFT_REDUCED = 2
    __OU_REDUCED = 4

    def __init__(self, torrent):
        super().__init__()
        self.pid = SSimulator().getNewPeerId()
        self._torrent = torrent
        self.__maxTFTSlots = 4
        self.__maxOUSlots = 1
        self.__nTFTSlots = 0
        self.__nOUSlots = 0
        self.__TFTSlotAge = 0
        self.__OUSlotAge = 0
        self.__minPeerListSize = 10 #TODO: change this to 30
        
        self.piecesQueue = set() #Set of pieces to download next
        
        self._peersConn = []
        self.__OUConn = []
        self.__OUReduced = set()
        self.__TFTConn = []
        self.__TFTReduced = set()
        self._peersReduced = set()
       
        self._isSeeder = False 

        self.registerSimFunction(Simulator.ST_UPDATE_LOCAL, self.updateLocalConnectionState )
        self.registerSimFunction(Simulator.ST_UPDATE_GLOBAL, self.updateGlobalConnectionState )
        self.registerSimFunction(Simulator.ST_LOGIC, self.peerLogic )
       
        self.__wasUnchocked = False
        #Start right away
        self.__TFTSlotAge = self.TFTPeriod
        self.__OUSlotAge = self.OUPeriod
    
    def __del__(self):
        Log.pLD("Peer is beeing destroyed")

    def __str__(self, *args, **kwargs):
        return "Peer [pid {0}, nid {1} ]".format(self.pid, self.nid)
    
    #Getting list of peer from tracker and add unknown ones to our own peer list 
    #Fills two lists
    #    self._peersReduced ... a simple list of peer id's of all known peers
    #    self._peersConn    ...     a list of tuples the form ( <download Rate>, <peer id>, <Connection>, <TTL> )
    def getNewPeerList(self):
        #print("Getting a new peer list from the tracker ...")
        newPeers = self._torrent.tracker.getPeerList()

        #Filter unwanted peers , for example itself
        def f(x): return ( x.pid != self.pid )
        newPeers = filter( f, newPeers )

        for i in newPeers :
            if i.pid in self._peersReduced :
                pass
            else:
            #except ValueError:                
                self._peersReduced.add(i.pid)
                newConnection = Connection(self, i)
                self._peersConn.append( (0,i.pid, newConnection, -1 ) )
                newConnection.connect()
                Log.pLD(self, "adding Peer [{0}]".format(i.pid))
    
    #Is called by a connection if there happens to be an unchock
    def unchockHappend(self):
        self.__wasUnchocked = True

    #Is called from an foreign peer to connect to this peer
    def connectToPeer(self, peer):
        #logging.log(Simulator.DEBUG, "[{0}] External peer is connecting! [{1}]".format(self.pid, peer.pid))
        Log.pLD(self, "External peer is connecting! [{0}]".format(peer.pid) )
        newConnection = None
            
        #If we already now this peer, return current connection
        if peer.pid in self._peersReduced :
            for i in self._peersConn:
                if( i[1] == peer.pid):
                    newConnection = i[2]
                    break
        else:
            Log.pLD(self, "adding Peer [{0}]".format(peer.pid))                
            self._peersReduced.add(peer.pid)
            newConnection = Connection(self, peer)
            self._peersConn.append( (0,peer.pid, newConnection, -1) )
            newConnection.connect()
        
        return newConnection 
            

    def updateLocalConnectionState(self):   
        
        if self._torrent.isFinished() == True :
            #So check if we want to leave or stay as a seeder
            if( self.__leaveTorrent() == True ):
                self._torrent.tracker.remPeer(self)
                self.__disconnectConnections()
                self.removeSimElement()
                Log.pLI(self, "Leaving torrent ...")
        else:
            if( (len(self.piecesQueue) < self.__minPieceInterestSize ) ):
                Log.pLD(self, "Getting new piece list for downloading ..." )
                self.piecesQueue = self.pieceSelection(self.__minPieceInterestSize*3) #Simulates the queuing of piece requests to other peers
        
        finishedPieces = self._torrent.getFinishedPieces()
        for i in self._peersConn :
            i[2].updateLocalState(finishedPieces)            

    
    def updateGlobalConnectionState(self):
        
        #Have to do this twice, because updateGlobalState() will remove disconnected peers from the peerConn list
        copy = list( self._peersConn )
        for i in copy :
            i[2].updateGlobalState()
        
        for i in self._peersConn:
            #try:
            idx = self._peersConn.index(i)
            #except ValueError:
            self._peersConn[idx] = (i[2].getDownloadRate(), i[1], i[2], i[3]) #Update the UploadRate field in the tuple
            if i[1] in self.__OUReduced:
                try:
                    idx = self.__OUConn.index(i)
                except ValueError:
                    idx = -1
                self.__OUConn[idx] = (i[2].getDownloadRate(), i[1], i[2], i[3])
            if i[1] in self.__TFTReduced:
                idx = self.__TFTConn.index(i)
                self.__TFTConn[idx] = (i[2].getDownloadRate(), i[1], i[2], i[3])
   
        #Some connection may have been chocked, if so free the slot and force a new OU or TFT algorithm call
        for i in self.__OUConn:
            if i[2].chocking == True:
                try:
                    idx = self._peersConn.index(i)
                except ValueError:
                    pass
                self._peersConn[idx] = ( i[0],i[1],i[2],-1 )
                idx = self.__OUConn.index(i)
                self.__OUConn[idx] = ( i[0],i[1],i[2],-1 )


        for i in self.__TFTConn:
            if i[2].chocking == True:
                #try:
                idx = self._peersConn.index(i)
                #except ValueError:
                #    pass
                self._peersConn[idx] = ( i[0],i[1],i[2],-1 )
                idx = self.__TFTConn.index(i)
                self.__TFTConn[idx] = ( i[0],i[1],i[2],-1 )

        self.__generateReducedSets(self.__OU_REDUCED | self.__TFT_REDUCED )

    def peerLogic(self):

        if(len(self._peersConn) < self.__minPeerListSize):
            self.getNewPeerList()
 
        self.__doChocking()

        #If not all TFT or OU slots are taken try to find peers
        if(self.__nOUSlots < self.__maxOUSlots):
            self.__OUSlotAge = self.OUPeriod
        if( self.__nTFTSlots < self.__maxTFTSlots ):
            self.__TFTSlotAge = self.TFTPeriod
       
        tftChoosen = list()
        ouChoosen = list()

        if(self._torrent.isFinished() == False):
            #Leecher
                        
            unusedSlots = 0
           
            if(self.__TFTSlotAge == self.TFTPeriod):
                tftChoosen = self.runTFT(self.__maxTFTSlots - self.__nTFTSlots)
                self.__TFTSlotAge = 0
                self.__TFTUnchock(tftChoosen)
                unusedSlots = self.__maxTFTSlots - self.__nTFTSlots - len(tftChoosen)
            
            if( (self.__OUSlotAge == self.OUPeriod) or (unusedSlots>0) ) : 
                ouChoosen = self.runOU(self.__maxOUSlots + unusedSlots - self.__nOUSlots)
                self.__OUSlotAge = 0
                self.__OUUnchock(ouChoosen)
            
            self.__TFTSlotAge += 1
            self.__OUSlotAge += 1
            
        else:
            #Seeder Part
            if( (self.__OUSlotAge == self.OUPeriod) or (self.__TFTSlotAge == self.TFTPeriod) ):
                nSlots = self.__maxOUSlots + self.__maxTFTSlots - self.__nOUSlots - self.__nTFTSlots
                if( nSlots > 0):
                    ouChoosen = self.runOU(nSlots)
                    self.__OUUnchock(ouChoosen)
                self.__OUSlotAge = 0
                
            self.__OUSlotAge += 1
        
        #Print statistics about the node
        self.__printStats()    

    def peerDisconnect(self, conn):

        #Remove connection from peer connection list, TFT and OU
        for i in self.__OUConn:
            if i[2] == conn:
                self.__OUConn.remove(i)
                self.__nOUSlots -= 1
                break

        for i in self.__TFTConn:
            if i[2] == conn:
                self.__TFTConn.remove(i)
                self.__nTFTSlots -= 1
                break

        for i in self._peersConn:
            if i[2] == conn:
                self._peersConn.remove(i)
                break

        self.__generateReducedSets(self.__PEER_REDUCED | self.__TFT_REDUCED | self.__OU_REDUCED )

        #Log.pLD(self, "Peer {0} disconnected ... ".format(conn.) )


    def __leaveTorrent(self):

        if self._isSeeder:
            return False

        i = random.random() * 100
        if ( i < 10 ) :
            return True
        else:
            return False

    def __disconnectConnections(self):
        for i in self._peersConn:
            i[2].disconnect()

        for idx,i in enumerate(self._peersConn) :
            self._peersConn[idx] = ( i[2].getDownloadRate(), i[1], i[2], i[3] ) 
        pass

    def __doChocking(self):
        t = SSimulator().tick

        #Chock OU
        for i in self.__OUConn:
            if i[3] <= t :
                i[2].chock()
                idx = self.__OUConn.index(i)
                self.__OUConn.pop(idx)

        #Chock TFT
        for i in self.__TFTConn:
            if i[3] <= t :
                i[2].chock()
                idx = self.__TFTConn.index(i)
                self.__TFTConn.pop(idx)
        
        self.__generateReducedSets(self.__OU_REDUCED | self.__TFT_REDUCED )

    def __OUUnchock(self, ouChoosen):

        t = SSimulator().tick

        #Unchock OU
        for i in ouChoosen:
            idx = self._peersConn.index(i)
            self._peersConn[idx] = (i[0],i[1],i[2],t + self.OUPeriod)
            self.__OUConn.append( self._peersConn[idx] )
            self._peersConn[idx][2].unchock(1024*20)
            

        self.__generateReducedSets(self.__OU_REDUCED)
    
    def __TFTUnchock(self, tftChoosen):

        t = SSimulator().tick

        #Unchock TFT
        for i in tftChoosen:
            #try:
            idx = self._peersConn.index(i)
            #except ValueError:
            #    pass

            self._peersConn[idx] = (i[0],i[1],i[2],t + self.TFTPeriod)
            self.__TFTConn.append( self._peersConn[idx] )
            self._peersConn[idx][2].unchock(1024*20)

        self.__generateReducedSets(self.__TFT_REDUCED)

    def __generateReducedSets(self, mode):

        if mode & self.__PEER_REDUCED:
            self._peersReduced = set()
            for i in self._peersConn:
                self._peersReduced.add(i[1])

        if mode & self.__TFT_REDUCED:
            self.__TFTReduced = set()
            for i in self.__TFTConn:
                self.__TFTReduced.add(i[1])
            self.__nTFTSlots = len(self.__TFTReduced)
        
        if mode & self.__OU_REDUCED:
            self.__OUReduced = set()
            for i in self.__OUConn:
                self.__OUReduced.add(i[1])
            self.__nOUSlots = len(self.__OUReduced)


    def __printStats(self):
       
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
        for i in self._peersConn:
            t.append( "( {0}@{1}/{2} {3}|{4}|{5}|{6} , {7})".format(i[1], \
                            i[2].getDownloadRate(),  \
                            i[2].getUploadRate(), \
                            1 if i[2].chocking == True else 0, \
                            1 if i[2].interested == True else 0, \
                            1 if i[2].peerIsChocking() == True else 0, \
                            1 if i[2].peerIsInterested() == True else 0, \
                            i[3], \
                            ) )

        Log.pLI(self, "DL {0}/{1} i{2} TFT {3}, OU {4} , PeerList {5}".format(self._torrent.getNumberOfFinishedPieces(), \
            self._torrent.getNumberOfPieces(), \
            len(self.piecesQueue), \
            self.__nTFTSlots, self.__nOUSlots, t) )
                        
    '''
        The Tit-for-tat algorithm ranks peers on their upload speed provided to this node.
        Take the <nSlots> highest ranked peers and execute the TFT algorithm on them 
    '''
    def runTFT(self, nSlots):
        Log.pLD(self, " Executing TFT Algorithm for {0}".format(nSlots) )
        #self._peersConn.sort() #Peer list in the form ( <UploadRate>, <PeerID>, <Connection> ) , sort will on the first field and on collision continue with the others
        
        choosen = list()
        candidates = self.getTFTCandidates()
        
        if(len(candidates) > 0):
            candidates.sort(reverse=True) #Sort candidates based on their uploadRate, (highest uploadRate first)
            if(nSlots > len(candidates)):
                nSlots = len(candidates)

            while(nSlots > 0):
                choosen.append( candidates.pop(0) )
                nSlots-=1
           
        if(nSlots > 0):
            Log.pLW(self, " not enough peers to fill all TFT slots ... {0} unfilled.".format(nSlots) )
        
        return choosen
        
    def runOU(self, nSlots):
        Log.pLD(self, "Executing OU Algorithm for {0}".format(nSlots) )
        #print("[{0}] peers [ {1} ]".format(self.pid, self._peersConn))
       
        #Skip if nothing to do
        if(nSlots == 0):
            return set()
       
        if(nSlots < 0):
            Log.pLE(self, "Error in calculating the number of OU slots to schedule. Will skip OU at this step!")
            return set()
       
        choosen = list()
        candidates = self.getOUCandidates()

        if( len(candidates) < nSlots ):
            Log.pLW(self, " not enough peers to populate all OU slots ... {0} unfilled.".format(nSlots - len(candidates)) )
            nSlots = len(candidates)      
        
        try:
            choosen = random.sample(candidates, nSlots)
        except ValueError:
            pass
        return choosen

    def finishedDownloadingPiece(self, conn, piece):
        self._torrent.finishedPiece( piece )
        if piece in self.piecesQueue:
            self.piecesQueue.remove(piece)

    def downloadingPiece(self, conn, piece):
        if piece in self.piecesQueue:
            self.piecesQueue.remove(piece)

    #Implementing Rarest piece first piece selection
    def pieceSelection(self, nPieces):
        emptyPieces = self._torrent.getEmptyPieces( self._torrent.getNumberOfPieces() )
        pieceHistogram = [ (0,x) for x in range(0, self._torrent.getNumberOfPieces()) ]
        for i in self._peersConn:
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

    def getUnchockedPeers(self):
        def f(x): return ( x[2].chocking == False )
        unchocked = list( filter( f, self._peersConn ) )
        return unchocked


    #Get a list of peers that we are currently not working with is not ourself  but have interest in us
    def getOUCandidates(self):
        def f(x): return ( ( x[2].peerIsInterested() == True ) and ( x[3] <= SSimulator().tick ) )
        candidates = list( filter( f, self._peersConn ) )
        return candidates

    #Get a list of peers that are interested in our data and have at least downloaded one slot ( either TFT or OU )
    def getTFTCandidates(self):
        def f(x): return ( ( x[0] > 0 ) and ( x[2].peerIsInterested() == True) and ( x[3] <= SSimulator().tick ) )
        candidates = list( filter( f, self._peersConn ) )
        return candidates
 
