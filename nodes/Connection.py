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
        self._averageDownloadRate = 0
        #self._maxDownloadRate = 0
        self._maxUploadRate = 0
        
        self.chocking = True
        self.interested = False
        self.disconnected = False

        self.finishedPieces = set()
       
        self._freshUnchock = False 
        self.__acumulatedData = 0
        self.finishedPieces = set()
        self.__currentPiece = -1
        self.__downloadablePieces = set()

        self.remoteConnection = None
   
    def disconnect(self):
        self.disconnected = True
        self.remoteConnection.disconnected = True

    def connect(self):
        #This is the connection element on the other side
        self.remoteConnection =  self.__destPeer.connectToPeer(self.__srcPeer)
    
    #Called by Peer to chock connection
    def chock(self):
        self.chocking = True
        self.__uploadRate = 0
        Log.pLD(self.__srcPeer, "chocking [{0}]".format(self.__destPeer.pid) )
        #self.__downloadRate = 0
        #self.remoteConnection.chockRemote()

    def setUploadLimit(self, rate):
        self._maxUploadRate = int(rate)
        self.__calculateUploadRate()
        
    #def setDownloadLimit(self, rate):
    #    self._maxDownloadRate = int(rate)
    def getUploadLimit(self):
        return self._maxUploadRate

    def getDownloadRate(self):
        return self.__downloadRate
    
    def getAverageDownloadRate(self):
        return self._averageDownloadRate
       
    #We upload data if we do not chock and the peer is interested 
    def getUploadRate(self):
        if( (self.chocking == False) and  (self.remoteConnection.interested == True) ):
            return self.__uploadRate
        else:
            return 0

    def unchock(self, uploadRate=-1):
        if(uploadRate > -1):
            self._maxUploadRate = int(uploadRate)
        #if(downloadRate > -1):
        #    self._maxDownloadRate = int(downloadRate)
        self.chocking = False
        Log.pLD(self.__srcPeer, "unchocking [{0}@{1}]".format(self.__destPeer.pid, self._maxUploadRate) )
        self.__calculateUploadRate()
        self._freshUnchock = True
        #self._averageDownloadRate = 0

    
    #Is called at the beginning of ervery tick and calculates the upload bandwidth for this tick for this connection
    def updateLocalState(self, finishedPieces):
        self.finishedPieces = finishedPieces
        self.__calculateUploadRate()
        #self.__calculateDownloadRate()

    #Have a simple up to 10% distortion rate
    def __calculateUploadRate(self):
        self.__uploadRate = self._maxUploadRate * ( 1.0 - ( random.random() % 0.1 ))
        self.__uploadRate = int(self.__uploadRate)

    #def __calculateDownloadRate(self):
    #    self.__downloadRate = self._maxDownloadRate * ( 1.0 - ( random.random() % 0.1 ))
    #    self.__downloadRate = int(self.__downloadRate)

    def peerIsInterested(self):
        return self.remoteConnection.interested

    def peerIsChocking(self):
        return self.remoteConnection.chocking

    '''
        This is called on every tick and has the following tasks:
            # Update interest and chock status for this connection
            # If a active download is going on, check for piece completion and assign new piece to download
    '''
    def updateGlobalState(self):

        if( self.disconnected == True ):
            #Connection was disconnected, tell peer
            self.__srcPeer.peerDisconnect(self)
            return

        #Check if we are seeding , if so, we are __NEVER__ interested
        if(self.__srcPeer.getTorrent().isFinished() == False):
        
            #Check what the other peer has to offer
            self.__calcDownloadablePieceSet()        
            if(len(self.__downloadablePieces) > 0):
                Log.pLD(self.__srcPeer, "Having interest in {0} from {1}".format( len(self.__downloadablePieces), self.__destPeer.pid) )
                self.interested = True
                self.__setCurrentPiece()
                #if( self.chocking == True ):
                #    self.unchock(self.__uploadRate, 0)
            else:
                Log.pLD(self.__srcPeer, "Loosing interest in peer {0}".format(self.__destPeer.pid) )
                #self.chocking = True
                self.interested = False
        else:
            self.interested = False
        
    def runDownload(self):
        #If nothing happens, nothing is downloaded
        self.__downloadRate = 0
        
        #Downloading happens if we are interested and the other peer is not chocking us
        if( (self.interested == True) and (self.remoteConnection.chocking == False) ):

            #Limit maximum download rate
            currentDownloadRate = self.remoteConnection.getUploadRate()
            currentDownloadRate = self.__srcPeer.requestDownloadBandwidth(currentDownloadRate)
            #if(currentDownloadRate > self._maxDownloadRate):
            #    currentDownloadRate = self._maxDownloadRate

            #Check if we finished a complete piece and if so mark it as finished and get the next one
            self.__acumulatedData += currentDownloadRate
           
            self.__downloadRate = currentDownloadRate
            
            #Make this int so we dont get too long floating number in output log
            self.__downloadRate = int(self.__downloadRate)
            
            Log.pLD(self.__srcPeer, "Downloaded {0}/{1} of piece {2}".format(self.__acumulatedData, self.__srcPeer.getTorrent().pieceSizeBytes, self.__currentPiece) )
            while(self.__acumulatedData > self.__srcPeer.getTorrent().pieceSizeBytes):
                Log.pLD(self.__srcPeer, "Finished downloading piece {0}".format(self.__currentPiece) )
            
                self.__srcPeer.finishedDownloadingPiece(self, self.__currentPiece )
                self.__acumulatedData -= self.__srcPeer.getTorrent().pieceSizeBytes
                self.__currentPiece = -1
                #Set a next piece and utilize the data downloaded for this one. If there are no more pieces discard the downloaded data
                if(self.__setCurrentPiece() == False):
                    self.__acumulatedData = 0   #This is simulating lost bandwidth due to running out of piece requests
                    Log.pLD(self.__srcPeer, "Piece request queue empty!" )
                    #On start of next round we will loose interest
                    #self.interested = False
            
            if(self.__currentPiece == -1):
                self.__setCurrentPiece()

        #Remote peer lost interest in us, stop sending data
        #if( self.chocking == False and self.remoteConnection.interested == False ):
        #    Log.pLD(self.__srcPeer, "Remote peer [{0}] lost interest, Chock!".format(self.__destPeer.pid) )
        #    self.chock()
                    
        #if( self.remoteConnection.chocking == True):
        #    self.__downloadRate = 0
        #    pass

    def postDownloadState(self):
        self.__uploadRate = self.remoteConnection.getDownloadRate() #Should be the real upload consumption
        
        #If the other peer was able to download this round, rate your download rate
        #if( (self.interested == True) and (self.remoteConnection.chocking == False) ):
        #If we unchock and this either a TFT or an OU Slot than take notice of our average download Rate 
        if( (self.chocking == False) and ( (self.__srcPeer._peersConn[self.__destPeer.pid][4] == 1) or (self.__srcPeer._peersConn[self.__destPeer.pid][4] == 2) ) ):
        #if( (self.chocking == False) and  (self.remoteConnection.interested == True) ):
            self._averageDownloadRate = int( ( self.__downloadRate + self._averageDownloadRate ) / 2 )
            '''
            if( self._averageDownloadRate == 0):
                self._averageDownloadRate = int(self.__downloadRate)
            else:
                if( self._freshUnchock == True ):
                    self._averageDownloadRate = self.__downloadRate
                    self._freshUnchock = False
                else:
                    self._averageDownloadRate = int( ( self.__downloadRate + self._averageDownloadRate ) / 2 )
            '''

    #Select a piece for downloading
    def __setCurrentPiece(self):
        self.__calcDownloadablePieceSet()

        if( len(self.__downloadablePieces) == 0):
            return False
        if( self.__currentPiece != -1):
            #Check if this piece is still available, if not choose a new one
            if self.__currentPiece in self.__downloadablePieces:
                Log.pLD(self.__srcPeer,"Still want piece {0} to from {1}".format(self.__currentPiece, self.__destPeer.pid) )
                return True #We already have a piece selected
    
        #shuffle the download list -> so we dont download the same piece from all peers
        self.__currentPiece = random.sample(self.__downloadablePieces, 1)[0]
        Log.pLD(self.__srcPeer,"Selecting piece {0} to get from {1}".format(self.__currentPiece, self.__destPeer.pid) )
        return True
    
    def __calcDownloadablePieceSet(self):
        self.__downloadablePieces = self.__srcPeer.piecesQueue & self.remoteConnection.finishedPieces   


