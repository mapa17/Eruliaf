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
    TFT_POSSIBLE_SLOT = 3

    def __init__(self, torrent, maxUploadRate, maxDownloadRate):
        super().__init__()
        self.pid = SSimulator().getNewPeerId()
        self._birth = SSimulator().tick
        self._torrent = torrent
        self._maxTFTSlots = 2
        self._maxOUSlots = 1
        self._nTFTSlots = 0
        self._nOUSlots = 0
        self._minPeerListSize = 30 #TODO: change this to 30
        self._maxDownloadRate = maxDownloadRate
        self._maxUploadRate = maxUploadRate
        self._activeDownloadBandwidthUsage = 0
        self._uploadRateLastTick = 0 #Upload rate calculated in _postLogic for each tick
        self._downloadRateLastTick = 0 #Download rate calculated in _postLogic for each tick

        self.piecesQueue = set() #Set of pieces to download next
        
        self._peersConn = {} #Empty dictionary key=peerID
       
        self._isSeeder = False 

        self.registerSimFunction(Simulator.ST_UPDATE_LOCAL, self.updateLocalConnectionState )
        self.registerSimFunction(Simulator.ST_UPDATE_GLOBAL, self.updateGlobalConnectionState )
        self.registerSimFunction(Simulator.ST_LOGIC, self.peerLogic )
        self.registerSimFunction(Simulator.ST_FILETRANSFER, self._runDownloads )
        self.registerSimFunction(Simulator.ST_CONCLUTION, self._conclutionState )
    
        self._runTFTFlag = True 
        self._runOUFlag = True
    
    def __del__(self):
        Log.pLD("Peer is being destroyed")

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
            

    #If we finished download, check if peer should stay in the swarm or leave
    #If the peer decides to stay, update locatelConnection state on every connection
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
        
        #Call updateLocalState() on each connection and update their averageDownloadRate
        finishedPieces = self._torrent.getFinishedPieces()
        for i in self._peersConn.values() :
            i[2].updateLocalState(finishedPieces)            

    
    def updateGlobalConnectionState(self):
        
        #Have to work on copy because updateGlobalState() will remove disconnected peers from the peerConn list
        copy = self._peersConn.copy()
        for i in copy.values() :
            i[2].updateGlobalState()
        
        t =  SSimulator().tick
        
        self._nOUSlots = 0
        self._nTFTSlots = 0
        
        for (k, v) in self._peersConn.items():
            #Terminate OU connections that lay waisted because the other side has no interest
            if (v[4] == self.OU_SLOT) and (v[2].peerIsInterested() == False):
                self._peersConn[k] = ( v[2].getAverageDownloadRate(), v[1], v[2], -1 , self.NO_SLOT)
                self._peersConn[k][2].chock()
                self._runOUFlag = True
            
            #Close TFT connections that we unchocked because we once had interest, but now we dont
            elif (v[4] == self.TFT_POSSIBLE_SLOT) and (v[2].interested == False):
                self._peersConn[k] = ( v[2].getAverageDownloadRate(), v[1], v[2], -1 , self.NO_SLOT)
                self._peersConn[k][2].chock()

            #If a possible better TFT got interested, run TFTAlgorithm
            elif (v[4] == self.TFT_POSSIBLE_SLOT) and (v[2].interested == True):
                self._runTFTFlag = True
                self._peersConn[k] = ( v[2].getAverageDownloadRate(), v[1], v[2], v[3] , v[4]) #Update the UploadRate field in the tuple
            
            #We have no interest, he has no interest, drop
            elif (v[4] == self.OU_SLOT) and (v[2].interested == False) and ( v[2].peerIsInterested() == False) :
                self._runOUFlag = True
                self._peersConn[k] = ( v[2].getAverageDownloadRate(), v[1], v[2], -1 , self.NO_SLOT) #Update the UploadRate field in the tuple    
            
            #We have no interest, he has no interest, drop
            elif (v[4] == self.TFT_SLOT) and (v[2].interested == False) and ( v[2].peerIsInterested() == False) :
                self._runTFTFlag = True
                self._peersConn[k] = ( v[2].getAverageDownloadRate(), v[1], v[2], -1 , self.NO_SLOT) #Update the UploadRate field in the tuple

            #A possible better TFT partner has become interested
            elif( (v[4] == self.TFT_POSSIBLE_SLOT) and ( v[2].peerIsInterested() == True) ):
                self._runTFTFlag = True
            
            #Chok connections who's TTL expired
            elif ( v[3] <= t )  :
                if ( v[4] == self.OU_SLOT) :
                    self._runOUFlag
                elif ( v[4] == self.TFT_SLOT) :
                    self._runTFTFlag
                    
                #In all cases, chock and TTL = 0
                self._peersConn[k] = ( v[2].getAverageDownloadRate(), v[1], v[2], -1 , self.NO_SLOT)
                self._peersConn[k][2].chock()
                
            else: #If nothing else, update uploadrate so the peer can be rated
                self._peersConn[k] = ( v[2].getAverageDownloadRate(), v[1], v[2], v[3] , v[4]) #Update the UploadRate field in the tuple
                
            if(v[4] == self.OU_SLOT):
                self._nOUSlots += 1
                
            if(v[4] == self.TFT_SLOT):
                self._nTFTSlots += 1

    def peerLogic(self):

        if(len(self._peersConn) < self._minPeerListSize):
            self.getNewPeerList()

        if(self._nTFTSlots < self._maxTFTSlots):
            self._runTFTFlag = True
                           
        if(self._nOUSlots < self._maxOUSlots):
            self._runOUFlag = True
             
        if(self._torrent.isFinished() == False):
            #Leecher
        
            self._findBetherTFTParnet()
         
            if( self._runTFTFlag == True):
                self._runTFTFlag = False
                nSlots = self._maxTFTSlots
                chosen = self.runTFT(nSlots)
            
            if( self._runOUFlag == True ):
                self._runOUFlag = False
                nSlots = self._maxOUSlots
                chosen = self.runOU(nSlots)
            
        else:
            #Seeder Part
            if( self._runOUFlag == True ):
                self._runOUFlag = False
                nSlots = self._maxOUSlots + self._maxTFTSlots
                chosen = self.runOU(nSlots)

    def _runDownloads(self):
        for i in self._peersConn.values() :
            i[2].runDownload()
            
    def _conclutionState(self):
        #Calculate the total upload and download usage
        self._downloadRateLastTick = 0
        self._uploadRateLastTick = 0
        for i in self._peersConn.values() :
            i[2].postDownloadState()
            self._downloadRateLastTick += i[2].getDownloadRate()
            self._uploadRateLastTick += i[2].getUploadRate() 
        
        #Print statistics about the node
        self._printStats()
    def _findBetherTFTParnet(self):
        #DONT KNOWWWoW, how often to run TFT, or bether how often to change peers
        pass
        
    #Is called by the connection passed as argument to tell the peer about a disconnected peer
    def peerDisconnect(self, conn):

        copy = self._peersConn.copy()
        for (k, v) in copy.items():
            if v[2] ==  conn:
#                if v[4] == self.OU_SLOT :
#                    self._nOUSlots -= 1
#                if v[4] == self.TFT_SLOT :
#                    self._nTFTSlots -=1
                del self._peersConn[k]
                break #The connection can only have existed once
                
        #Log.pLD(self, "Peer {0} disconnected ... ".format(conn.) )

    #Called by local connection to allocate download bandwidth
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

    
#    def _doChocking(self):
#        t = SSimulator().tick
#
#        for i in self._peersConn.values() :
#            if i[3] <= t :
#                '''
#                #Only call chock on open connections
#                if i[4] == self.OU_SLOT :
#                    self._nOUSlots -= 1
#                    i[2].chock()
#                if i[4] == self.TFT_SLOT :
#                    self._nTFTSlots -=1
#                    i[2].chock()
#                '''
#                if (i[4] == self.OU_SLOT) or (i[4] == self.TFT_SLOT):
#                    i[2].chock()                    
#                    self._peersConn[i[1]] = ( i[0],i[1],i[2], -1, self.NO_SLOT )

#    def _OUUnchock(self, ouChoosen):
#
#        #Unchock OU
#        for i in ouChoosen:
#            self._peersConn[i[1]] = i
#            self._nOUSlots += 1
#            self._peersConn[i[1]][2].unchock()
#    
#    def _TFTUnchock(self, tftChoosen):
#
#        #Unchock TFT
#        for i in tftChoosen:
#            self._peersConn[i[1]] = i
#            self._nTFTSlots += 1
#            self._peersConn[i[1]][2].unchock()
            
    def _printStats(self):
       
        #Print PeerList
        t = []
        for i in self._peersConn.values():
            t.append( "( {0}@{1}/{2}/{3} {4}|{5}|{6}|{7} , {8}|{9})".format(i[1], \
                            i[2].getUploadRate(), \
                            i[2].getDownloadRate(),  \
                            i[2].getAverageDownloadRate(), \
                            1 if i[2].chocking == True else 0, \
                            1 if i[2].interested == True else 0, \
                            1 if i[2].peerIsChocking() == True else 0, \
                            1 if i[2].peerIsInterested() == True else 0, \
                            i[3], \
                            "N" if i[4] == self.NO_SLOT else "T" if i[4] ==  self.TFT_SLOT else "P" if i[4] ==  self.TFT_POSSIBLE_SLOT else "O", \
                            ) )

        Log.pLI(self, "[{8}] DL {0}/{1} i{2} TFT {3}/{4}, OU {5}/{6} , U/D [{9}/{10}], PeerList {7}".format(self._torrent.getNumberOfFinishedPieces(), \
            self._torrent.getNumberOfPieces(), \
            len(self.piecesQueue), \
            self._nTFTSlots, self._maxTFTSlots, \
            self._nOUSlots, self._maxOUSlots, \
            t, \
            self.__class__.__name__, \
            self._uploadRateLastTick, self._downloadRateLastTick \
            ) )
                        
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
            #if(nSlots > len(candidates)):
            #    nSlots = len(candidates)

            while( (len(chosen) < nSlots) and (len(candidates) > 0) ):
                p = candidates.pop(0)
                
                #Only unchok peers that are not already unchocked!
                if( (p[4] != self.TFT_SLOT) and (p[2].peerIsInterested() == True) ):
                    self._peersConn[p[1]] = ( p[0], p[1], p[2], t + self.TFTPeriod, self.TFT_SLOT )
                    self._peersConn[p[1]][2].unchock()    
                    chosen.append(p[1])
                    
                #This a possible peering partner, unchock
                if( (p[4] != self.TFT_SLOT) and (p[2].peerIsInterested() == False) ):
                    self._peersConn[p[1]] = ( p[0], p[1], p[2], t + self.TFTPeriod, self.TFT_POSSIBLE_SLOT )
                    self._peersConn[p[1]][2].unchock()                    
        
            
        #If not all FTF Slots have been used, try with any peer that has interest, regardless of their upload( similar to OU just shorter slots)           
        if( len(chosen) < nSlots):
            Log.pLI(self, "Not enough real TFT candidates, will try less proper peers".format() )
            
            candidates = list()
            for i in self._peersConn.values():    
                if(( i[2].peerIsInterested() == True ) and ( i[4] == self.NO_SLOT) ):
                    candidates.append(i[1])
            
            unusedSlots = nSlots - len(chosen)
            unusedSlots = min(unusedSlots, len(candidates))
            sample = list( random.sample(candidates, unusedSlots ) )
            for i in sample:
                p = self._peersConn[i]
                self._peersConn[i] = ( p[0], p[1], p[2], t + self.TFTPeriod, self.TFT_SLOT )
                self._peersConn[i][2].unchock()
                chosen.append(i)
        
        #Do chocking of all TFT peers that currently are unchocked but not have been chosen in this round
        for p in self._peersConn.values():
            if( (p[4] == self.TFT_SLOT) and (chosen.count(p[1]) == 0) ):
                self._peersConn[p[1]] = ( p[0], p[1], p[2], -1, self.NO_SLOT )
                self._peersConn[p[1]][2].chock()
   
        self._nTFTSlots = len(chosen)
        return chosen
        
    def runOU(self, nSlots):
        Log.pLD(self, "Executing OU Algorithm for {0}".format(nSlots) )
        #print("[{0}] peers [ {1} ]".format(self.pid, self._peersConn))
       
        t = SSimulator().tick
        chosen = list()
       
        #Calculate the number of current OU Slots and possible candidates that are interested but not in OU or TFT
        candidates = [] #Array of peerId
        
        for i in self._peersConn.values():
            
            #Add peers which are already in OU
            if( i[4] == self.OU_SLOT ):
                chosen.append(i[1])
                
            if(( i[2].peerIsInterested() == True ) and ( i[4] != self.TFT_SLOT) ):
                candidates.append(i[1])
       

        unusedSlots = nSlots - len(chosen)
        if( unusedSlots > 0 ):
            unusedSlots = min(unusedSlots, len(candidates) ) #Cant select more than there are
            t1 = list( random.sample(candidates, unusedSlots) )
            for i in t1:
                p = self._peersConn[i]
                self._peersConn[i] = ( p[0], p[1], p[2], t + self.OUPeriod, self.OU_SLOT )
                self._peersConn[i][2].unchock()
                chosen.append(p[1]) 
                
        elif( unusedSlots < 0):
            #There are too many OU slots taken, remove some by random
            unusedSlots = unusedSlots * (-1)
            t1 = list( random.sample(chosen, unusedSlots ) )
            for i in t1:
                p = self._peersConn[i]
                self._peersConn[i] = ( p[0], p[1], p[2], -1, self.NO_SLOT )
                self._peersConn[i][2].chock()
                chosen.remove(p[1])
        
        self._nOUSlots = len(chosen) 
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


    #Get a list of peers that we are currently not downloading in OU or TFT and are interested to receive data
#    def getOUCandidates(self):
#        #def f(x): return ( ( x[2].peerIsInterested() == True ) and ( x[3] <= SSimulator().tick ) )
#        #candidates = list( filter( f, self._peersConn ) )
#        t = SSimulator().tick
#        candidates = list()
#        for i in self._peersConn.values():
#            if(( i[2].peerIsInterested() == True ) and ( i[3] <= t) ):
#                candidates.append(i)
#
#        return candidates

    #Get a list of peers that we are interested in, not matter about their interest or chock status
    #Skip peers which already run in OU and peers that have not uploaded anything (new peers for example)
    #Skip peers to which we have never uploaded anything
    def getTFTCandidates(self):
        #def f(x): return ( ( x[0] > 0 ) and ( x[2].peerIsInterested() == True) and ( x[3] <= SSimulator().tick ) )
        #candidates = list( filter( f, self._peersConn ) )
        
        candidates = list()
        for i in self._peersConn.values():
            if( ( i[2].interested == True ) and ( i[4] != self.OU_SLOT ) and ( i[0] > 0 ) ):
            #if( ( i[4] != self.OU_SLOT ) and ( i[0] > 0 ) ):
                candidates.append(i)

        return candidates
 
