'''
Created on Feb 14, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''

from nodes.Node import Node
from simulation.SSimulator import SSimulator
from nodes.Connection import Connection
import random
from simulation.Simulator import Simulator
from utils.Log import Log
from nodes.Peer import Peer
from simulation.SConfig import SConfig
import math

class Peer_C1(Peer):
    def __init__(self, torrent, maxUploadRate, maxDownloadRate):
        super().__init__(torrent, maxUploadRate, maxDownloadRate)

        self._leaveRate = float( SConfig().value("LeaveRate", "PeerC1") )

        #self.__slotUploadRate = maxUploadRate / 16 
        self._maxTFTSlots = 0
        self._maxOUSlots = 16

        #Start right away
        self._TFTPhaseCnter = 0
        self._OUPhaseCnter = 0

        self._TFTSlotList = list()
        self._OUSlotList = list()
        
        #Reduce the OU Period from 30 in the BitTorrent Specification to 10 
        self.OUPeriod = 10
        
        self._maxOUUploadRate = 0
        self._maxTFTUploadRate = 0

    def __str__(self, *args, **kwargs):
        return "Peer_C1 [pid {0}]".format(self.pid)

    def updateLocalConnectionState(self):
        
        if( self._getMorePeersFlag == True):
            self._dropPeers(self._maxPeerListSize - 20) #Drop some peers to have space for new ones
            
        super().updateLocalConnectionState()

    #Override Prelogic to decide when to start TFT and OU algorithm and how long ease phase runs
    def _preLogicOperations(self):
        
        t = SSimulator().tick

        if(len(self._peersConn) < self._minPeerListSize):
            self._getMorePeersFlag = True

        if(self._getMorePeersFlag == True):
            self._getMorePeersFlag = False
            self.getNewPeerList()
        

        if(self._torrent.isFinished() == False):
            #Leecher
                
            #TFT and OU Have to be called together because the maximal upload usage depends on each other        
            if( (self._nextOUPhaseStart == t) or (self._nextTFTPhaseStart == t) ):

                (self._maxTFTSlots, self._maxOUSlots, self._maxTFTUploadRate, self._maxOUUploadRate ) = self._calculateSlotCountAndUploadRate( self._pieceAvailability , self._OUPhaseCnter)                 

                self._OUPhaseCnter += 1
                self._nextOUPhaseStart = t + self.OUPeriod
                self._runOUFlag = True

 
                self._TFTPhaseCnter += 1
                self._nextTFTPhaseStart = t + self.TFTPeriod
                self._runTFTFlag = True

        else:
            #Seeder Part
            if( self._nextOUPhaseStart == t):
                self._maxOUSlots = self._OUPhaseCnter%4 + 1
                self._nextOUPhaseStart = t + self.OUPeriod
                self._maxOUUploadRate = self._maxUploadRate 
                self._runOUFlag = True
                
            
        #Print statistics about the node
        #self._printStats()    

    #Simply chosen nSlotElement nodes and distributes the OU Upload equally between them
    def runOU(self, nSlots, TTL):
        #if(nSlots == 0):
        #    return list()
        #return chosen #DO NOT RETURN HERE OR THE CHOCKING AT THE END OF THE FUNCTION WONT BE APPLIED
    
        if(nSlots < 0):
            raise(ValueError)
        
        #Calculate bandwidth for OU and than for every slot
        #uploadBandWidth = self._maxUploadRate * ( self._maxOUSlots / (self._maxOUSlots + self._maxTFTSlots) )
        uploadBandWidth = self._maxOUUploadRate / self._maxOUSlots
        
        #Run the normal OU and than modify the upload limit and the ttl of the connection
        chosen = self._runOU(nSlots, TTL)
        for idx in chosen:
            self._peersConn[idx][2].setUploadLimit(uploadBandWidth)
        
        return chosen

    #Slightly modified OU algorithm that prefers interested peers over a complete random peer 
    def _runOU(self, nSlots, TTL):
        Log.pLD(self, "Executing OU Algorithm for {0}".format(nSlots) )
        #print("[{0}] peers [ {1} ]".format(self.pid, self._peersConn))
       
        t = SSimulator().tick
        chosen = list()
       
        #Calculate the number of current OU Slots and possible candidates that are interested but not in OU or TFT
        candidates = self.getOUCandidates()
        if(len(candidates) < nSlots):
            self._getMorePeersFlag = True
            nSlots = len(candidates)
            #if(nSlots == 0):
            #    return chosen
            #DO NOT RETURN HERE OR THE CHOCKING AT THE END OF THE FUNCTION WONT BE APPLIED
        
        #candidates = random.sample(candidates, len(candidates)) #Array of peerId
        random.shuffle(candidates)
        candidates2 = list(candidates)
        
        while( (len(chosen) < nSlots) and (len(candidates) > 0) ):
            p = candidates.pop(0)
            
            #Prefer interested peers
            if( p[2].peerIsInterested() == False):
                continue

            #Only unchok peers that are not already unchoked!
            if( (p[4] != self.OU_SLOT) ):
                self._peersConn[p[1]][2].unchock()    
            
            self._peersConn[p[1]] = ( p[0], p[1], p[2], TTL, self.OU_SLOT )
            chosen.append(p[1])
        
        #If there are not enough interested peers, take some random peers
        if(len(chosen) < nSlots):
            self._getMorePeersFlag = True #Do more/better peer discovery
            candidates = candidates2
            while( (len(chosen) < nSlots) and (len(candidates) > 0) ):
                p = candidates.pop(0)
                
                #Dont add peers twice
                if( (p[1] in chosen) == True):
                    continue
    
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



    #Solve a continuous Knapsack problem with value being the downloadRate and weight the upload Rate
    #Solution is a simply greedy one. Order peers depending on their Rating and chose as many as possible to either
    #Fill up the download rate or the number of slots
    def runTFT(self, nSlots, TTL):
        
        candidates = self.getTFTCandidates()
        if len(candidates) == 0:
            self._getMorePeersFlag = True
            #return list() #DO NOT RETURN HERE OR THE CHOCKING AT THE END OF THE FUNCTION WONT BE APPLIED
        
        #Create a list of tuples, or peer rating and peer id
        #Rate peers depending on their download/upload ration. New peers get a ration of zero (worst) , maybe change this to one?
        rated = []
        for (idx,i) in enumerate(candidates) :
            if( i[2].getUploadLimit() == 0):
                rated.append( (0, idx) )
            else:
                rated.append( (i[0] / i[2].getUploadLimit() , idx) )

        rated.sort(reverse=True)
        rated2 = list(rated) #Copy the rated list for later
       
        chosen = []
         
        #This will be set earlier by self._calculateSlotCountAndUploadRate()
        maxUpload = self._maxTFTUploadRate
        acUploadRate = 0

        #nSlots = min(nSlots, len(rated))
        while( (acUploadRate < maxUpload ) and (len(chosen) < nSlots) and (len(rated) > 0) ):
            idx = rated.pop(0)[1] #Index of the elements in candidates
            p = candidates[idx] 
            
            #Skip peers that would take too much upload
            if( (acUploadRate + p[2].getUploadLimit()) > maxUpload ):
                continue
            
            #Only unchok peers that are not already unchocked!
            if(p[4] != self.TFT_SLOT):
                self._peersConn[p[1]][2].unchock()
            
            self._peersConn[p[1]] = ( p[0],p[1],p[2], TTL , self.TFT_SLOT )
            chosen.append(p[1])
            acUploadRate += p[2].getUploadLimit()
        
        #If we are not able to use all our upload capacity something is wrong. Do more peer discovery -> get more peers
        restOfUploadBandwidth = maxUpload - acUploadRate
        if(restOfUploadBandwidth>100):
            self._getMorePeersFlag = True
            #Take another peer and limit the upload to the available bandwidth
            rated = rated2
            while( (acUploadRate < maxUpload ) and (len(chosen) < nSlots) and (len(rated) > 0) ):
                idx = rated.pop()[1] #Index of the elements in candidates
                p = candidates[idx] 
                    
                #Skip peers that would take too much upload
                if( p[1] in chosen ):
                    continue
                
                #Only unchok peers that are not already unchocked!
                if(p[4] != self.TFT_SLOT):
                    self._peersConn[p[1]][2].unchock()
                
                p[2].setUploadLimit(restOfUploadBandwidth)#Important
                
                self._peersConn[p[1]] = ( p[0],p[1],p[2], TTL , self.TFT_SLOT )
                chosen.append(p[1])
                acUploadRate += p[2].getUploadLimit()
                
        #Do chocking of all TFT peers that currently are unchocked but not have been chosen in this round
        for i in self._peersConn.values():
            if( (i[4] == self.TFT_SLOT) and (chosen.count(i[1]) == 0) ):
                self._peersConn[i[1]] = ( i[0], i[1], i[2], -1, self.NO_SLOT )
                self._peersConn[i[1]][2].chock()
        
        Log.pLD(self, " Executed modified TFT Algorithm and selected {0} peers".format( len(chosen) ) )
        self._nTFTSlots = len(chosen)
        
        return chosen

    def _calculateUploadRate(self, connection):
        if(self._torrent.isFinished() == False):
            return self._maxUploadRate / 3 
        else:
            return -1

    def _calculateSlotCountAndUploadRate(self, pieceAvailability, ouPhaseCnter):
        nMaxTFTSlots = 0
        nMaxOUSlots = 0
        
        x = pieceAvailability
        
        #Add some random behavior
        x += random.randint(-5,5);
        if( x < 0): x = 0
        if( x > 100): x = 100
       
        # http://www.wolframalpha.com/input/?i=plot%7B+int%28+atan%280.05%28x-10%29%29+*+10.0+%29+%2C+int%28+%288+-+%28%28+atan%280.15*x+-+2%29+*+0.5+%29+%2B+0.5%29*4%29+%2B+1%29%7D+%2C+x+%3D+%5B0%2C100%5D
        nMaxTFTSlots = int( math.atan(0.05*(x-10)) * 10 )
        if(nMaxTFTSlots <= 0): nMaxTFTSlots = 1
        nMaxOUSlots = int( (8 - (( math.atan(0.15*x - 2) * 0.5 ) + 0.5)*4) + 1)
        
        #Calculate max upload rates per connection . Simple separation of upload depending on the number of slots.
        #This does not mean that each TFT or OU connection gets the same upload bandwidth. Its limiting absolute bandwidth only!
        maxTFTUpload = ( self._maxUploadRate * ( nMaxTFTSlots / (nMaxTFTSlots + nMaxOUSlots) ) )
        maxOUUpload = ( self._maxUploadRate * ( nMaxOUSlots / (nMaxTFTSlots + nMaxOUSlots) ) )
        
        
        #On top of this, put a vibration on the OU slots in order to have a peer discovery with different upload bandwidth to find cheap and expesive peers
        if(x > 15):
            nMaxOUSlots = nMaxOUSlots / ((ouPhaseCnter  % 4) + 1) #Circulate nMaxOUSlots between 1 and 4 slots
            nMaxOUSlots = int(nMaxOUSlots)

            
        return (nMaxTFTSlots, nMaxOUSlots, maxTFTUpload, maxOUUpload)
    
    def _dropPeers(self, maxPeers):
        p = list(self._peersConn)
        nDrop = len(p) - maxPeers
        if(nDrop < 0):
            return #Nothing to do
        
        while(nDrop > 0):
            pID = random.sample(p, 1)[0]
            #print("Dropping peer {} from {}".format(pID, p))
            p.remove(pID)
                
            c = self._peersConn[pID]
            if(c[4] != Peer.NO_SLOT):
                continue #Do not drop active connection of any kind
            
            self._peersConn[pID][2].disconnect()
            nDrop-=1

    #def _calculateDownloadRate(self, connection):
    #    return self._maxDownloadRate / ( self._maxTFTSlots + self._maxOUSlots ) 


