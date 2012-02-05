'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''
from nodes.Node import Node
from simulation.SSimulator import SSimulator
from nodes.Connection import Connection
import random

class Peer(Node):

    pid = -1
    #__torrent = None
    #__activeTFTPeers = []
    #__activeOUPeers = []
    #__idlePeers = []
    #__blockedPeers = []
    #__peers = []
    #__peersReduced = []
    __TFTPeriod = 10    # number of ticks a TFT slot is active
    __OUPeriod = 30     # number of ticks a UO slot is active
    __minPieceInterestSize =  30

    def __init__(self, torrent):
        super().__init__()
        self.pid = SSimulator().getNewPeerId()
        self.__torrent = torrent
        self.__maxTFTSlots = 3
        self.__maxOUSlots = 1
        self.__nTFTSlots = 0
        self.__nOUSlots = 0
        self.__TFTSlotAge = 0
        self.__OUSlotAge = 0
        self.__minPeerListSize = 1 #TODO: change this to 30
        
        self.__nextPieces = set() #Set of pieces to download next
        
        self.__peers = []
        self.__peersReduced = []
        
        self.registerSimFunction(0, self.updateConnections )
        self.registerSimFunction(1, self.peerLogic )        
        
    def __str__(self, *args, **kwargs):
        return "Peer [pid {0}, nid {1} ]".format(self.pid, self.nid)
    
    #Getting list of peer from tracker and add unknown ones to our own peer list 
    #Fills two lists
    #    self.__peersReduced ... a simple list of peer id's of all known peers
    #    self.__peers    ...     a list of tuples the form ( <download Rate>, <peer id>, <Connection> )
    def getNewPeerList(self):
        #print("Getting a new peer list from the tracker ...")
        newPeers = self.__torrent.tracker.getPeerList()
        
        for i in newPeers :
            try:
                self.__peersReduced.index(i.pid)
            except ValueError:                
                self.__peersReduced.append(i.pid)
                newConnection = Connection(self, i)
                self.__peers.append( (0,i.pid, newConnection) )
                newConnection.connect()
                print("[{0}] adding Peer [{1}]".format(self.pid, i.pid))
                

    #Is called from an foreign peer to connect to this peer
    def connectToPeer(self, peer):
        print("[{0}] External peer is connecting! [{1}]".format(self.pid, peer.pid))
        newConnection = None
        try:
            #If we already now this peer, return current connection
            self.__peersReduced.index(peer.pid)
            for i in self.__peers:
                if( i[1] == peer.pid):
                    newConnection = i[2]
                    break
        
        except ValueError:
            print("[{0}] adding Peer [{1}]".format(self.pid, peer.pid))                
            self.__peersReduced.append(peer.pid)
            newConnection = Connection(self, peer)
            self.__peers.append( (0,peer.pid, newConnection) )
            newConnection.connect()
        
        return newConnection 
            

#    def getConnection(self, peerID):
#        try:
#            self.__peersReduced.index(peerID)
#            for i in self.__peers:
#                if( i[1] == peerID):
#                    return i[2] 
#        except ValueError:                
#            print("[{0}] requesting a connection to a unkown peer [{1}]".format(self.pid, peerID))
#            
#        return None

    def updateConnections(self):
        finishedPieces = self.__torrent.getFinishedPieces()
        for i in self.__peers :
            i[2].update(finishedPieces, self.__nextPieces)
            i = (i[2].getDownloadRate(), i[1], i[2]) #Update the UploadRate field in the tuple
    
    def peerLogic(self):
        
        if(len(self.__peers) < self.__minPeerListSize):
            self.getNewPeerList()
        
        if(self.__torrent.isFinished() == False):
            #Leecher
            if( len(self.__nextPieces) < ( self.__minPieceInterestSize ) ):
                self.pieceSelection(self.__minPieceInterestSize * 2)
                
            self.__TFTSlotAge += 1
            self.__OUSlotAge += 1
            
            if(self.__OUSlotAge == self.__OUPeriod):
                self.runOU(self.__maxOUSlots)
                self.__OUSlotAge = 0
            
            if(self.__TFTSlotAge == self.__TFTPeriod):
                unusedSlots = self.runTFT(self.__maxTFTSlots)
                if(unusedSlots > 0):
                    #Use this slots for OU
                    self.runOU(unusedSlots)
                self.__TFTSlotAge = 0
        else:
            #Seeder Part
            self.runOU(self.__maxOUSlots + self.__maxTFTSlots)
            
            
    '''
        The Tit-for-tat algorithm ranks peers on their upload speed provided to this node.
        Take the <nSlots> highest ranked peers and execute the TFT algorithm on them 
    '''
    def runTFT(self, nSlots):
        print("Executing TFT Algorithm for {0}".format(nSlots) )
        self.__peers.sort() #Peer list in the form ( <UploadRate>, <PeerID>, <Connection> ) , sort will on the first field and on collision continue with the others
        
        #Get a list of peers that provided some upload
        def f(x): return ( ( x[0] > 0 ) and ( x[1] != self.pid ) )
        candidates = filter( f, self.__peers )
        
        for i in candidates :
            i[2].transferData()
            nSlots-=1
            if(nSlots == 0):
                break;
        
        if(nSlots > 0):
            print("[{0}] not enough peers to fill all TFT slots ... {1} unfilled.".format(self.pid,nSlots) )
        
        return nSlots
        
    def runOU(self, nSlots):
        print("Executing OU Algorithm for {0}".format(nSlots) )
        #print("[{0}] peers [ {1} ]".format(self.pid, self.__peers))
        
        #Get a list of peers that have either not uploaded anything yet or just unchocked us
        def f(x): return ( ( x[0] == 0 ) and ( x[1] != self.pid ) )
        candidates = list( filter( f, self.__peers ) )

        if( len(candidates) < nSlots ):
            print("[{0}] not enough peers to populate all OU slots ... {1} unfilled.".format(self.pid,nSlots - len(candidates)) )
            nSlots = len(candidates)      
            
        candidates = random.sample(candidates, nSlots)

        for i in candidates :
            i[2].transferData(1000)
            
    def pieceSelection(self, nPieces):
        self.__nextPieces = set( self.__torrent.getEmptyPieces(nPieces) )
    
    def getTorrent(self):
        return self.__torrent
    
    #def getBestPeers(self):
        
        
            