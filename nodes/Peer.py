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
from simulation.SConfig import SConfig

class Peer(Node):

    pid = -1
    TFTPeriod = 10    # number of ticks a TFT slot is active
    OUPeriod = 30     # number of ticks a UO slot is active

    NO_SLOT = -1
    TFT_SLOT = 1
    OU_SLOT = 2
    TFT_POSSIBLE_SLOT = 3

    def __init__(self, torrent, maxUploadRate, maxDownloadRate, sleepTime):
        maxUploadRate = int(maxUploadRate)
        maxDownloadRate = int(maxDownloadRate)
        super().__init__()
        self.pid = SSimulator().getNewPeerId()
        self._downloadStart = SSimulator().tick
        self._downloadEnd = -1
        self._torrent = torrent
        self._maxTFTSlots = 4
        self._maxOUSlots = 1
        self._nTFTSlots = 0
        self._nOUSlots = 0
        self._minPeerListSize = 30
        self._maxPeerListSize = 55 #This is only used in order to not call the Tracker for new peers. This is not limiting other peers to connect to this one
        self._maxDownloadRate = maxDownloadRate
        self._maxUploadRate = maxUploadRate
        self._activeDownloadBandwidthUsage = 0
        self._uploadRateLastTick = 0 #Upload rate calculated in _postLogic for each tick
        self._downloadRateLastTick = 0 #Download rate calculated in _postLogic for each tick
        self._timeBetweenPeerListUpdates = 20 #At most update Peer List every 20 ticks
        self._lastPeerListUpdate = (-1) * self._timeBetweenPeerListUpdates #set this so that in Tick 0 peers can update their peer list
        
        #Keep track of downloaded data
        self._TFTByteUpload = 0
        self._TFTByteDownload = 0
        self._OUByteUpload = 0
        self._OUByteDownload = 0

        self.piecesQueue = list() #Set of pieces to download next
        
        #A hash table with a tuple for every known neighbor.
        #Key is the peer id and the value is in the form <DownloadRate> <PeerID> <Ref to Connection> <TTL> <Connection Type>
        self._peersConn = {} #Empty dictionary key=peerID
       
        self._leaveRate = float( SConfig().value("LeaveRate", "Peer") )
        self._leaveNextRound = False
       
        self._isSeeder = False
        
        self._runTFTFlag = True 
        self._runOUFlag = True
 
        self._getMorePeersFlag = True
        
        self._pieceRandomizeCount = 50 #The 50 most rarest pieces will be download at random
        self._pieceAvailability = 0.0 #Every time we call piece selection, as well calculate the average file completion of all our neighbors
        
        self._sleepTime = sleepTime

        self.registerSimFunction(Simulator.ST_INIT, self._wakeUpPeer )
           
    def __del__(self):
        Log.pLD("Peer is being destroyed")

    def __str__(self, *args, **kwargs):
        return "Peer [pid {0}, nid {1} ]".format(self.pid, self.nid)
   
    def _wakeUpPeer(self):
        
        if( self._sleepTime > 0):
            self._sleepTime -= 1
            return
        
        Log.pLD(self, "Node waking up ...".format())
        
        #Unregister sleep and setup peer for normal operation
        self.unregisterSimFunction(Simulator.ST_INIT, self._wakeUpPeer )
        
        self.registerSimFunction(Simulator.ST_UPDATE_LOCAL, self.updateLocalConnectionState )
        self.registerSimFunction(Simulator.ST_UPDATE_GLOBAL, self.updateGlobalConnectionState )
        self.registerSimFunction(Simulator.ST_LOGIC, self.peerLogic )
        self.registerSimFunction(Simulator.ST_FILETRANSFER, self._runDownloads )
        self.registerSimFunction(Simulator.ST_CONCLUTION, self._conclutionState )

        #Decide when to run tft and ou algorithm next time
        self._nextTFTPhaseStart = SSimulator().tick
        self._nextOUPhaseStart = SSimulator().tick
        self._nextPieceQueueUpdate = SSimulator().tick
        
        #Register to tracker
        self._torrent.tracker.connect(self)
   
    #Getting list of peer from tracker and add unknown ones to our own peer list 
    def getNewPeerList(self):
        
        #Dont create too many connections to other peers ( because of performance problems )        
        if(len(self._peersConn) >= self._maxPeerListSize):
            return
        t = SSimulator().tick
        if( (t - self._lastPeerListUpdate) < self._timeBetweenPeerListUpdates):
            return
        else:
            self._lastPeerListUpdate = t
        
        Log.pLD(self, "Ask Tracker for new peers ...".format())
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

        if(self._leaveNextRound == True):
            self._torrent.tracker.remPeer(self)
            self._disconnectConnections()
            self.removeSimElement()
            Log.pLI(self, "Leaving torrent ...")
            
        if self._torrent.isFinished() == True :
            if( self._downloadEnd == -1):
                self._downloadEnd = SSimulator().tick
            #So check if we want to leave or stay as a seeder
            if( self._leaveTorrent() == True ):
                self._leaveNextRound = True #Leave next round, if not, the peer wont be seen by the observer as finished!
        else:
            if( (SSimulator().tick >= self._nextPieceQueueUpdate)  or (len(self.piecesQueue) == 0) ):
                Log.pLD(self, "Getting new piece list for downloading ..." )
                (self.piecesQueue, self._pieceAvailability) = self.pieceSelection(self._pieceRandomizeCount) #Simulates the queuing of piece requests to other peers
                self._nextPieceQueueUpdate = SSimulator().tick + 5 #Shedule next update
        
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
               
            #If nothing else, update uploadrate so the peer can be rated
            self._peersConn[v[1]] = ( v[2].getAverageDownloadRate(), v[1], v[2], v[3] , v[4]) #Update the UploadRate field in the tuple
                
            if(v[4] == self.OU_SLOT):
                self._nOUSlots += 1
                
            if(v[4] == self.TFT_SLOT):
                self._nTFTSlots += 1
    

    def _preLogicOperations(self):
        
        t = SSimulator().tick
        
        if(len(self._peersConn) < self._minPeerListSize):
            self._getMorePeersFlag = True
        
        if(self._getMorePeersFlag == True):
            self._getMorePeersFlag = False
            self.getNewPeerList()

        if( self._nextTFTPhaseStart <= t):
            self._nextTFTPhaseStart = t + self.TFTPeriod
            self._runTFTFlag = True

        if( self._nextOUPhaseStart <= t):
            self._nextOUPhaseStart = t + self.OUPeriod
            self._runOUFlag = True

        if(self._nTFTSlots < self._maxTFTSlots):
            self._runTFTFlag = True
                           
        if(self._nOUSlots < self._maxOUSlots):
            self._runOUFlag = True
         
    '''
    How the un/chok algorithm should work
    
    The maxTFTSlot peers should be unchoked for 10sec and left to them to download/request pieces
    These peers are selected based on their short term upload rate (not averaging too much) best, two time slots
    
    I think i can niglect this unchoking of better nodes (possible tft peers), because in order to download form them
    the only thing i need is interest. If the other peer unchoks I can donwload, and by doing so rate the peer.
    
    I think its best to have synchronized tft slots, meaning all tft should be selected at once.
    
    Going back to the first implementation! 
    '''
                
    def peerLogic(self):
        self._preLogicOperations()
   
        if(self._sleepTime > 0):
            self._sleepTime -= 1
            return
    
        if( (self._runOUFlag == True) or (self._runTFTFlag == True) ):
            printChosen = True
            tftChosen = []
            ouChosen = []
        else:
            printChosen = False
    
        if(self._torrent.isFinished() == False):
            #Leecher
        
            if( self._runTFTFlag == True):
                self._runTFTFlag = False
                nSlots = self._maxTFTSlots
                tftChosen = self.runTFT(nSlots, self._nextTFTPhaseStart)
            
            if( self._runOUFlag == True ):
                self._runOUFlag = False
                nSlots = self._maxOUSlots
                ouChosen = self.runOU(nSlots, self._nextOUPhaseStart)
            
        else:
            #Seeder Part
            if( self._runOUFlag == True ):
                self._runOUFlag = False
                nSlots = self._maxOUSlots + self._maxTFTSlots
                ouChosen = self.runOU(nSlots, self._nextOUPhaseStart)
                nSlots = 0
                tftChosen = self.runTFT(0, 0)
                
        if(printChosen == True):
            Log.pLI(self, "TFTChosen {} until {}, OUChosen {} until {}".format( tftChosen, self._nextTFTPhaseStart, ouChosen, self._nextOUPhaseStart ) )
                                                     

    def _runDownloads(self):
        for i in self._peersConn.values() :
            i[2].runDownload()
            
    def _conclutionState(self):
        #Calculate the total upload and download usage
        self._downloadRateLastTick = 0
        self._uploadRateLastTick = 0
        
        self._TFTByteDownload = 0
        self._TFTByteUpload = 0
        self._OUByteDownload = 0
        self._OUByteUpload = 0
        
        for i in self._peersConn.values() :
            #Let the connection calculate how much it send and received
            i[2].postDownloadState()
            
            down = i[2].getDownloadRate()
            up = i[2].getUploadRate()
            
            #Accumulate for statistics the mount of data send or received, and if it was on a TFT or OU slot
            if( (i[4] == self.TFT_SLOT) or (i[4] == self.TFT_POSSIBLE_SLOT) ):
                self._TFTByteDownload += down
                self._TFTByteUpload += up
            else:
                self._OUByteDownload += down
                self._OUByteUpload += up
                
            self._downloadRateLastTick += down
            self._uploadRateLastTick += up
        
        #Print statistics about the node
        self._printStats()
        
    #Is called by the connection passed as argument to tell the peer about a disconnected peer
    def peerDisconnect(self, conn):

        copy = self._peersConn.copy()
        for (k, v) in copy.items():
            if v[2] ==  conn:
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

        i = random.random()
        if ( i < self._leaveRate ) :
            return True
        else:
            return False

    def _disconnectConnections(self):
        for i in self._peersConn.values():
            i[2].disconnect()

    
    def _printStats(self):
       
        #Print PeerList
        t = []
        for i in self._peersConn.values():
            t.append( "( {0}@{1}/{2}/{3} {4}|{5}|{6}|{7} , {8}|{9})".format(i[1], \
                            i[2].getUploadRate(), \
                            i[2].getDownloadRate(),  \
                            i[0], \
                            #i[2].getAverageDownloadRate(), \
                            1 if i[2].chocking == True else 0, \
                            1 if i[2].interested == True else 0, \
                            1 if i[2].peerIsChocking() == True else 0, \
                            1 if i[2].peerIsInterested() == True else 0, \
                            i[3], \
                            "N" if i[4] == self.NO_SLOT else "T" if i[4] ==  self.TFT_SLOT else "P" if i[4] ==  self.TFT_POSSIBLE_SLOT else "O", \
                            ) )

        Log.pLI(self, "[{}] DL {}/{} i{} pA{} TFT {}/{}, OU {}/{} , U/D [{}/{}], PeerList {}".format( self.__class__.__name__, \
            self._torrent.getNumberOfFinishedPieces(), \
            self._torrent.getNumberOfPieces(), \
            len(self.piecesQueue), \
            self._pieceAvailability, \
            self._nTFTSlots, self._maxTFTSlots, \
            self._nOUSlots, self._maxOUSlots, \
            self._uploadRateLastTick, self._downloadRateLastTick,  \
            t ) )
        
    '''
        The Tit-for-tat algorithm ranks peers on their upload speed provided to this node.
        Take the <nSlots> highest ranked peers and execute the TFT algorithm on them 
        
        It depends only on their upload rate, not any interest on their or our part. If we have no
        interest our download will be low/zero and so we will rate the peer as useless in the next slot.
    '''
    def runTFT(self, nSlots, TTL):
        Log.pLD(self, " Executing TFT Algorithm for {0}".format(nSlots) )
        #self._peersConn.sort() #Peer list in the form ( <UploadRate>, <PeerID>, <Connection> ) , sort will on the first field and on collision continue with the others
        
        t = SSimulator().tick
        chosen = list()
        
        #Now everyone is a candidate, take even current OU Slots, this makes sense to step up a peer from OU to TFT is they are good
        candidates = self.getTFTCandidates()
        
        if(len(candidates) == 0):
            self._getMorePeersFlag = True
            #return chosen #DO NOT RETURN HERE OR THE CHOCKING AT THE END OF THE FUNCTION WONT BE APPLIED
        
        candidates.sort(reverse=True) #Sort candidates based on their uploadRate, (highest uploadRate first)

        shuffledFlag = False
        while( (len(chosen) < nSlots) and (len(candidates) > 0) ):
            p = candidates.pop(0)
            
            #If all the rest of the peers have zero upload, shuffle them
            if((p[0] == 0) and (shuffledFlag == False)):
                shuffledFlag = True #Only shuffle once
                candidates.append(p)
                candidates = random.sample(candidates, len(candidates)) #Array of peerId
                p = candidates.pop(0)
            
            #Only unchok peers that are not already unchoked!
            if( (p[4] != self.TFT_SLOT) ):
                self._peersConn[p[1]][2].unchock()    
            
            self._peersConn[p[1]] = ( p[0], p[1], p[2], TTL, self.TFT_SLOT )
            chosen.append(p[1])
        
        #Do chocking of all TFT peers that currently are unchocked but not have been chosen in this round
        for p in self._peersConn.values():
            if( (p[4] == self.TFT_SLOT) and (chosen.count(p[1]) == 0) ):
                self._peersConn[p[1]] = ( p[0], p[1], p[2], -1, self.NO_SLOT )
                self._peersConn[p[1]][2].chock()
   
        self._nTFTSlots = len(chosen)
        return chosen
    
    #Simply get one peer that is not currently in a FTF slot and run OU 
    def runOU(self, nSlots, TTL):
        Log.pLD(self, "Executing OU Algorithm for {0}".format(nSlots) )
        #print("[{0}] peers [ {1} ]".format(self.pid, self._peersConn))
       
        t = SSimulator().tick
        chosen = list()
       
        #Calculate the number of current OU Slots and possible candidates that are interested but not in OU or TFT
        candidates = self.getOUCandidates()
        if(len(candidates) < nSlots):
            self._getMorePeersFlag = True
            nSlots = len(candidates)
            if(nSlots == 0):
                return chosen
        
        candidates = random.sample(candidates, len(candidates)) #Array of peerId
        
        while( len(chosen) < nSlots ):
            p = candidates.pop(0)
            
            #Only unchok peers that are not already unchoked!
            if( (p[4] != self.OU_SLOT) ):
                self._peersConn[p[1]][2].unchock()    
            
            self._peersConn[p[1]] = ( p[0], p[1], p[2], TTL, self.OU_SLOT )
            chosen.append(p[1])
            
        #Do chocking of all OU peers that currently are unchoked but not have been chosen in this round
        for p in self._peersConn.values():
            if( (p[4] == self.OU_SLOT) and (chosen.count(p[1]) == 0) ):
                self._peersConn[p[1]] = ( p[0], p[1], p[2], -1, self.NO_SLOT )
                self._peersConn[p[1]][2].chock()
                
        self._nOUSlots = len(chosen) 
        return chosen

    def finishedDownloadingPiece(self, conn, piece):
        self._torrent.finishedPiece( piece )
        if piece in self.piecesQueue:
            self.piecesQueue.remove(piece)

    def downloadingPiece(self, piece):
        if piece in self.piecesQueue:
            self.piecesQueue.remove(piece)

    #Implementing Rarest piece first piece selection
    def pieceSelection(self, nRarePieces):
        
        avgPieceAvailability = 0.0
        
        nPieces = self._torrent.getNumberOfPieces()        
        emptyPieces = self._torrent.getEmptyPieces()
        
        #First value is our own
        avgPieceAvailability = (nPieces - len(emptyPieces)) / nPieces
        
        pieceHistogram = [ (0,x) for x in range(0, nPieces) ]
        for i in self._peersConn.values():
            #Get a set of finished pieces
            fp = i[2].remoteConnection.finishedPieces
            
            avgPieceAvailability += len(fp) / nPieces #Sum up averages
            
            candidates =  fp & emptyPieces
            for k in candidates:
                pieceHistogram[k] = ( pieceHistogram[k][0] + 1, pieceHistogram[k][1])

        #Filter elements that no one has
        #def f(x): return ( x[0] != 0 )
        #pieceHistogram = list( filter(f, pieceHistogram ) )
        temp = []
        for i in pieceHistogram:
            if(i[0] > 0):
                temp.append(i)
        pieceHistogram = temp
        #Sort the histogram on the number of counts of finished pieces, least common are at the beginning
        pieceHistogram.sort()

        #Shuffle the nRarestPieces of the piece List in order not everyone tries to get the same piece
        if nRarePieces > len(pieceHistogram):
            nRarePieces = len(pieceHistogram)
        
        rarestPieces = list()
        for i in range(nRarePieces) :
            rarestPieces.append(pieceHistogram.pop(0))
            
        random.shuffle(rarestPieces)
        
        #Join the sets again
        while(len(rarestPieces) > 0):
            pieceHistogram.insert(0,rarestPieces.pop(0))
        
        selection = list()
        #Now extract the piece Index and return
        for i in pieceHistogram:
            selection.append(i[1])

        avgPieceAvailability = avgPieceAvailability / (len(self._peersConn) + 1)        
        #Return as a set the ordered pieces to download the ( nRarePieces ) pieces are randomized 
        return selection, int(avgPieceAvailability*100.0)

    def getTorrent(self):
        return self._torrent

    #def getUnchockedPeers(self):
    #    def f(x): return ( x[2].chocking == False )
    #    unchocked = list( filter( f, self._peersConn ) )
    #    return unchocked


    #Simply convert the peer list to a array and through away peers that are already in TFT Slots
    def getOUCandidates(self):
        candidates = list()
        for i in self._peersConn.values():
            if(i[4] == self.TFT_SLOT):
                continue
            
            candidates.append(i)

        return candidates

    #Simply convert the peer dictionary to an array 
    def getTFTCandidates(self):
        candidates = list()
        for i in self._peersConn.values():
            candidates.append(i)

        return candidates
 
