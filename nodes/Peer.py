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
    __minPieceInterestSize =  50

    def __init__(self, torrent):
        super().__init__()
        self.pid = SSimulator().getNewPeerId()
        self.__torrent = torrent
        self.__maxTFTSlots = 1
        self.__maxOUSlots = 0
        self.__nTFTSlots = 0
        self.__nOUSlots = 0
        self.__TFTSlotAge = 0
        self.__OUSlotAge = 0
        self.__minPeerListSize = 1 #TODO: change this to 30
        
        self.__nextPieces = set() #Set of pieces to download next
        
        self.__peersConn = []
        self.__OUConn = []
        self.__OUReduced = set()
        self.__TFTConn = []
        self.__TFTReduced = set()
        self.__peersReduced = []
        
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
    #    self.__peersReduced ... a simple list of peer id's of all known peers
    #    self.__peersConn    ...     a list of tuples the form ( <download Rate>, <peer id>, <Connection>, <TTL> )
    def getNewPeerList(self):
        #print("Getting a new peer list from the tracker ...")
        newPeers = self.__torrent.tracker.getPeerList()

        #Filter unwanted peers , for example itself
        def f(x): return ( x.pid != self.pid )
        newPeers = filter( f, newPeers )

        for i in newPeers :
            try:
                self.__peersReduced.index(i.pid)
            except ValueError:                
                self.__peersReduced.append(i.pid)
                newConnection = Connection(self, i)
                self.__peersConn.append( (0,i.pid, newConnection, -1 ) )
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
        try:
            #If we already now this peer, return current connection
            self.__peersReduced.index(peer.pid)
            for i in self.__peersConn:
                if( i[1] == peer.pid):
                    newConnection = i[2]
                    break
        
        except ValueError:
            Log.pLD(self, "adding Peer [{0}]".format(peer.pid))                
            self.__peersReduced.append(peer.pid)
            newConnection = Connection(self, peer)
            self.__peersConn.append( (0,peer.pid, newConnection, 0) )
            newConnection.connect()
        
        return newConnection 
            

    def updateLocalConnectionState(self):
        finishedPieces = self.__torrent.getFinishedPieces()
        for i in self.__peersConn :
            i[2].updateLocalState(finishedPieces, self.__nextPieces)
            i = (i[2].getDownloadRate(), i[1], i[2]) #Update the UploadRate field in the tuple
    
    def updateGlobalConnectionState(self):
        for i in self.__peersConn :
            i[2].updateGlobalState()
    
    def peerLogic(self):
        
        if(len(self.__peersConn) < self.__minPeerListSize):
            self.getNewPeerList()
 
        self.__doChocking()

        #If not all TFT or OU slots are taken try to find peers
        if(self.__nOUSlots < self.__maxOUSlots):
            self.__OUSlotAge = self.OUPeriod
        if( (self.__nTFTSlots < self.__maxTFTSlots) or (self.__wasUnchocked == True) ):
            self.__TFTSlotAge = self.TFTPeriod
            #self.__wasUnchocked = False
       
        tftChoosen = list()
        ouChoosen = list()

        if(self.__torrent.isFinished() == False):
            #Leecher
            #if( len(self.__nextPieces) < ( self.__minPieceInterestSize ) ):
            self.pieceSelection(self.__minPieceInterestSize) #Simulates the queuing of piece requests to other peers
            
            unusedSlots = 0
           
            if(self.__TFTSlotAge == self.TFTPeriod):
                tftChoosen = self.runTFT(self.__maxTFTSlots - self.__nTFTSlots)
                unusedSlots = self.__maxTFTSlots - self.__nTFTSlots - len(tftChoosen)
                self.__TFTSlotAge = 0
            
            if(self.__OUSlotAge == self.OUPeriod):
                ouChoosen = self.runOU(self.__maxOUSlots + unusedSlots - self.__nOUSlots)
                self.__OUSlotAge = 0
            
            self.__TFTSlotAge += 1
            self.__OUSlotAge += 1
            
        else:
            #Seeder Part
            if( (self.__OUSlotAge == self.OUPeriod) or (self.__TFTSlotAge == self.TFTPeriod) ):
                nSlots = self.__maxOUSlots + self.__maxTFTSlots - self.__nOUSlots - self.__nTFTSlots
                if( nSlots > 0):
                    ouChoosen = self.runOU(nSlots)
                self.__OUSlotAge = 0
                
            self.__OUSlotAge += 1
        
        #Chock/Unchock peers, update peer lists
        self.__doUnchock(ouChoosen, tftChoosen)

        #Print statistics about the node
        self.__printStats()    

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
        
        self.__TFTReduced = set()
        for i in self.__TFTConn:
            self.__TFTReduced.add(i[1])
        self.__nTFTSlots = len(self.__TFTReduced)
        
        self.__OUReduced = set()
        for i in self.__OUConn:
            self.__OUReduced.add(i[1])
        self.__nOUSlots = len(self.__OUReduced)


    def __doUnchock(self, ouChoosen, tftChoosen):

        t = SSimulator().tick

        #Unchock OU
        for i in ouChoosen:
            idx = self.__peersConn.index(i)
            self.__peersConn[idx] = (i[0],i[1],i[2],t + self.OUPeriod)
            self.__OUConn.append( self.__peersConn[idx] )
            self.__peersConn[idx][2].unchock(1024*20)

        #Unchock TFT
        for i in tftChoosen:
            idx = self.__peersConn.index(i)
            self.__peersConn[idx] = (i[0],i[1],i[2],t + self.OUPeriod)
            self.__TFTConn.append( self.__peersConn[idx] )
            self.__peersConn[idx][2].unchock(1024*20)

        self.__TFTReduced = set()
        for i in self.__TFTConn:
            self.__TFTReduced.add(i[1])
        self.__nTFTSlots = len(self.__TFTReduced)
        
        self.__OUReduced = set()
        for i in self.__OUConn:
            self.__OUReduced.add(i[1])
        self.__nOUSlots = len(self.__OUReduced)

 
    def __printStats(self):
       
        '''
        #Print list of unchocked peers
        def f(x): return ( x[2].chocking==False )
        candidates = filter( f, self.__peersConn )
        reduced = []
        for i in candidates:
            reduced.append(i[1])
        Log.pLD(self, "Unchocked peers {0}".format(reduced) )
        '''

        #Print OU Candidates
        #Log.pLD(self, "OU Candidates {0}".format( self.getOUCandidates() ) )

        #Print PeerList
        t = []
        for i in self.__peersConn:
            t.append( "( {0}@{1} , {2}|{3}|{4}|{5} , {6})".format(i[1],i[0], \
                            1 if i[2].chocking == True else 0, \
                            1 if i[2].interested == True else 0, \
                            1 if i[2].peerIsChocking() == True else 0, \
                            1 if i[2].peerIsInterested() == True else 0, \
                            i[3], \
                            ) )

        Log.pLD(self, "TFT {0}, OU {1} , PeerList {2}".format(self.__nTFTSlots, self.__nOUSlots, t) )
                        
        #Print download status
        Log.pLD(self, "Downloaded {0}/{1} Pieces".format(self.__torrent.getNumberOfFinishedPieces(), self.__torrent.getNumberOfPieces()) )

    '''
        The Tit-for-tat algorithm ranks peers on their upload speed provided to this node.
        Take the <nSlots> highest ranked peers and execute the TFT algorithm on them 
    '''
    def runTFT(self, nSlots):
        Log.pLD(self, " Executing TFT Algorithm for {0}".format(nSlots) )
        #self.__peersConn.sort() #Peer list in the form ( <UploadRate>, <PeerID>, <Connection> ) , sort will on the first field and on collision continue with the others
        
        choosen = list()
        candidates = self.getTFTCandidates()

        if(len(candidates) > 0):
            candidates = candidates.sort(reverse=True) #Sort candidates based on their uploadRate, (highest uploadRate first)
            if(nSlots > len(candidates)):
                nSlots = len(candidates)

            while(nSlots > 0):
                choosen = candidates.pop(0)
                nSlots-=1
       
        if(nSlots > 0):
            Log.pLW(self, " not enough peers to fill all TFT slots ... {0} unfilled.".format(nSlots) )
        
        return choosen
        
    def runOU(self, nSlots):
        Log.pLD(self, "Executing OU Algorithm for {0}".format(nSlots) )
        #print("[{0}] peers [ {1} ]".format(self.pid, self.__peersConn))
       
        choosen = list()
        candidates = self.getOUCandidates()

        if( len(candidates) < nSlots ):
            Log.pLW(self, " not enough peers to populate all OU slots ... {0} unfilled.".format(nSlots - len(candidates)) )
            nSlots = len(candidates)      
            
        choosen = random.sample(candidates, nSlots)
        return choosen

    def pieceSelection(self, nPieces):
        self.__nextPieces = set( self.__torrent.getEmptyPieces(nPieces) )
    
    def getTorrent(self):
        return self.__torrent

    def getUnchockedPeers(self):
        def f(x): return ( x[2].chocking == False )
        unchocked = list( filter( f, self.__peersConn ) )
        return unchocked


    #Get a list of peers that we are currently not working with is not ourself  but have interest in us
    def getOUCandidates(self):
        def f(x): return ( ( x[2].peerIsInterested() == True ) and ( x[3] <= SSimulator().tick ) )
        candidates = list( filter( f, self.__peersConn ) )
        return candidates

    #Get a list of peers that are interested in our data and have at least downloaded one slot ( either TFT or OU )
    def getTFTCandidates(self):
        def f(x): return ( ( x[0] > 0 ) and ( x[2].peerIsInterested() == True) and ( x[3] <= SSimulator().tick ) )
        candidates = list( filter( f, self.__peersConn ) )
        return candidates
 
