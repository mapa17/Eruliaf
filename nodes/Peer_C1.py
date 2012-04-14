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

    def __str__(self, *args, **kwargs):
        return "Peer_C1 [pid {0}]".format(self.pid)

    #Override Prelogic to decide when to start TFT and OU algorithm and how long ease phase runs
    def _preLogicOperations(self):
        
        t = SSimulator().tick

        if(len(self._peersConn) < self._minPeerListSize):
            self.getNewPeerList()


        if(self._torrent.isFinished() == False):
            #Leecher
            
            if( self._nextOUPhaseStart == t):
                
                if(self._OUPhaseCnter < 3):
                    self._nextOUPhaseStart = t + (self.OUPeriod / 3) #In the bootstrap phase use OU soly for discovery not altruistic, for that make OU Period shorter
                    self._maxOUSlots = int( 16 / 2**self._OUPhaseCnter) # 16,8,4
                    self._maxTFTSlots = 0
                else:
                    self._nextOUPhaseStart = t + self.OUPeriod
                    self._maxOUSlots = self._OUPhaseCnter%4 + 1
                    self._maxTFTSlots = 12
                    
                self._OUPhaseCnter += 1
                self._runOUFlag = True

 
            if( self._nextTFTPhaseStart == t):
                self._TFTPhaseCnter += 1
                self._nextTFTPhaseStart = t + self.TFTPeriod
                self._runTFTFlag = True

            else:
                #Normal Mode
                self._runOUFlag = True
                self._runTFTFlag = True 
        else:
            #Seeder Part
            if( self._nextOUPhaseStart == t):
                self._maxOUSlots = self._OUPhaseCnter%4 + 1
                self._nextOUPhaseStart = t + self.OUPeriod
                self._runOUFlag = True
                
            
        #Print statistics about the node
        #self._printStats()    

    #Simply chosen nSlotElement nodes and distributes the OU Upload equally between them
    def runOU(self, nSlots, TTL):
        if(nSlots == 0):
            return list()
    
        if(nSlots < 0):
            raise(ValueError)
        
        #Calculate bandwidth for OU and than for every slot
        #uploadBandWidth = self._maxUploadRate * ( self._maxOUSlots / (self._maxOUSlots + self._maxTFTSlots) )
        if( self._maxOUSlots > 4):
            uploadBandWidth = self._maxUploadRate * ( self._maxOUSlots / (self._maxOUSlots + self._maxTFTSlots) )
        else:
            uploadBandWidth = self._maxUploadRate * ( 4 / (4 + self._maxTFTSlots) )
        uploadBandWidth /= self._maxOUSlots
        
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
            if(nSlots == 0):
                return chosen
        
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
        
        if(nSlots == 0):
            return list()
        
        candidates = self.getTFTCandidates()
        if len(candidates) == 0:
            self._getMorePeersFlag = True
            return list()

        rated = []
        for (idx,i) in enumerate(candidates) :
            if( i[2].getUploadLimit() == 0):
                rated.append(0, idx)
            else:
                rated.append( (i[0] / i[2].getUploadLimit() , idx) )

        rated.sort()
       
        chosen = []
         
        #Always calculate with 4 OU Slots
        #maxUpload = ( self._maxUploadRate * ( self._maxTFTSlots/(self._maxTFTSlots + self._maxOUSlots) ) )
        maxUpload = ( self._maxUploadRate * ( self._maxTFTSlots/(self._maxTFTSlots + 4) ) )
        acUploadRate = 0

        #nSlots = min(nSlots, len(rated))

        while( (acUploadRate < maxUpload ) and (len(chosen) < nSlots) and (len(rated) > 0) ):
            idx = rated.pop()[1] #Index of the elements in candidates
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
        
        #If we are not able to use all our upload capacity something is wrong. Maybe we have a too small neighborhood; -> get more peers
        if(acUploadRate < maxUpload):
            self._getMorePeersFlag = True
        
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

    #def _calculateDownloadRate(self, connection):
    #    return self._maxDownloadRate / ( self._maxTFTSlots + self._maxOUSlots ) 


