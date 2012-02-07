'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''
import random
#from simulation.Simulator import Simulator
from utils.Log import Log

class Connection(object):
    
    __srcPeer = None
    __destPeer = None
    
    def __init__(self, src, dest):
        self.__srcPeer = src
        self.__destPeer = dest
        self.__uploadRate = 0
        self.__downloadRate = 0
        self.__connectionTime = 0 #Number of ticks this connection is exchanging data
        
        self.chocking = True
        self.interested = False
        
        self.finishedPieces = set()
        self.interestingPieces = set()
        
        self.__acumulatedData = 0
        self.finishedPieces = set()
        self.interestingPieces = set()
        self.__nextPieces = set()
        self.__currentPiece = -1
        
        self.__remoteConnection = None
    
    def connect(self):
        #This is the connection element on the other side
        self.__remoteConnection =  self.__destPeer.connectToPeer(self.__srcPeer)
    
    #Called by Peer to chock connection
    def chock(self):
        self.chocking = True
        self.__uploadRate = 0
        self.__downloadRate = 0
        self.__remoteConnection.chockRemote()

    #Called from remote connection when chocking
    def chockRemote(self):
        #If for some reason we are not transferring data any more, halt everything and reset the download state of this piece
        Log.pLD(self.__srcPeer,"Chocked from remote peer. ChockStatus [ {0} {1} ]".format(self.chocking, self.__remoteConnection.chocking ) )
        self.__downloadRate = 0
        #Mark the active piece as empty again! and discard what has been downloaded
        if( self.__currentPiece != -1 ):
            self.__srcPeer.getTorrent().setEmptyPiece(self.__currentPiece)
            self.__currentPiece = -1
            self.__acumulatedData = 0


    def unchock(self, uploadRate):
        Log.pLD(self.__srcPeer, "unchocking [{0}@{1}]".format(self.__destPeer.pid, uploadRate) )
        self.chocking = False #Next update() call will select piece ( so first second is downloading but what is defined later. This simulates that the wanted pieces are already selected earlier
        self.__uploadRate = uploadRate
        self.__connectionTime = 0
        self.__setCurrentPiece()
        self.__remoteConnection.unchockRemote()
   
    #Is called from remoteConnection when it unchocks this peer
    def unchockRemote(self):
        self.__srcPeer.unchockHappend()

    '''
        This is called with stage 0 on every tick and has the following tasks:
            # Update interest and chock status for this connection
            # If a active download is going on, check for piece completion and assign new piece to download
    '''
    def updateLocalState(self, finishedPieces, interestingPieces):
        self.finishedPieces = finishedPieces
        self.interestingPieces = interestingPieces
        
        self.__uploadRate = self.__uploadRate # dont modify this right now, later simulate fluctuation
    
    def peerIsInterested(self):
        return  self.__remoteConnection.interested

    def peerIsChocking(self):
        return self.__remoteConnection.chocking

    def updateGlobalState(self):
        #Check if we are seeding , if so, we are __NEVER__ interested
        if(self.__srcPeer.getTorrent().isFinished() == False):
        
            #Check what the other peer has to offer
            self.__nextPieces = self.interestingPieces & self.__remoteConnection.finishedPieces
            if(len(self.__nextPieces) > 0):
                Log.pLD(self.__srcPeer, "Getting interest in peer {0}".format(self.__destPeer.pid) )
                self.interested = True
                if( self.chocking == True ):
                    self.unchock(self.__uploadRate)
            else:
                Log.pLD(self.__srcPeer, "Loosing interest in peer {0} , therefore chocking conn.".format(self.__destPeer.pid) )
                self.chocking = True
                self.interested = False
        else:
            self.interested = False
            return #As seeder return here, if uploaded or not is defined by the peer logic
        
        if(self.chocking == True):
            return #If we have this connection chocked, there is nothing else to process
        
        #If both are unchocked and we need something from the other side, set a current piece
        #if( self.chocking == False and self.interested == True and self.__remoteConnection.chocking == False):
        if( self.chocking == False and self.__remoteConnection.chocking == False):
        
            self.__connectionTime += 1
        
            #shuffle the download list -> so we dont download the same piece from all peers
            self.__nextPieces = random.sample(self.__nextPieces, len(self.__nextPieces))
        
            #Check if we finished a complete piece and if so mark it as finished and get the next one
            self.__downloadRate = self.__remoteConnection.getUploadRate()
            self.__acumulatedData += self.__downloadRate
            
            self.__downloadRate /= self.__connectionTime
            
            Log.pLD(self.__srcPeer, "Downloaded {0}/{1} of piece {2}".format(self.__acumulatedData, self.__srcPeer.getTorrent().pieceSizeBytes, self.__currentPiece) )
            while(self.__acumulatedData > self.__srcPeer.getTorrent().pieceSizeBytes):
                Log.pLD(self.__srcPeer, "Finished downloading piece {0}".format(self.__currentPiece) )
                self.__srcPeer.getTorrent().finishedPiece( self.__currentPiece )
                self.__acumulatedData -= self.__srcPeer.getTorrent().pieceSizeBytes
                self.__currentPiece = -1
                #Set a next piece and utilize the data downloaded for this one. If there are no more pieces discard the downloaded data
                if(self.__setCurrentPiece() == False):
                    self.__acumulatedData = 0   #This is simulating lost bandwidth due to running out of piece requests
                    Log.pLD(self.__srcPeer, "Piece request queue empty!" )
                    return  
            
            if(self.__currentPiece == -1):
                self.__setCurrentPiece()
            
    #Select a piece for downloading
    def __setCurrentPiece(self):
    
        if( len(self.__nextPieces) == 0):
            return False
        if( self.__currentPiece != -1):
            Log.pLD(self.__srcPeer,"Still want piece {0} to from {1}".format(self.__currentPiece, self.__destPeer.pid) )
            return True #We allready have a piece slected

        self.__currentPiece = self.__nextPieces.pop()
        self.__srcPeer.getTorrent().downloadPiece(self.__currentPiece)
        Log.pLD(self.__srcPeer,"Selecting piece {0} to get from {1}".format(self.__currentPiece, self.__destPeer.pid) )
        return True
        
    def getDownloadRate(self):
        return self.__downloadRate
    
    def setUploadRate(self, rate):
        self.__uploadRate = rate
        
    #called from other connection
    def getUploadRate(self):
        return self.__uploadRate
