'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''
import random
#from simulation.Simulator import Simulator
from utils.Log import Log

class Connection(object):

    _srcPeer = None
    _destPeer = None
        
    def __init__(self, src, dest):
        self._srcPeer = src
        self._destPeer = dest

        self._uploadRate = 0
        self._downloadRate = 0
        self._lastDownloadRate = 0
        self._averageDownloadRate = 0
        #self._maxDownloadRate = 0
        self._maxUploadRate = 0
        
        self.chocking = True
        self.interested = False
        self.disconnected = False

       
        self._freshUnchock = False 
        self._acumulatedData = 0
        self.finishedPieces = set()
        self._currentPiece = -1
        self._downloadablePieces = set()

        self.remoteConnection = None
   
    def disconnect(self):
        self.disconnected = True
        self.remoteConnection.disconnected = True

    def connect(self):
        #This is the connection element on the other side
        self.remoteConnection =  self._destPeer.connectToPeer(self._srcPeer)
    
    #Called by Peer to chock connection
    def chock(self):
        self.chocking = True
        self._uploadRate = 0
        Log.pLD(self._srcPeer, "chocking [{0}]".format(self._destPeer.pid) )
        #self._downloadRate = 0
        #self.remoteConnection.chockRemote()

    def setUploadLimit(self, rate):
        self._maxUploadRate = int(rate)
        self.__calculateUploadRate()
        
    #def setDownloadLimit(self, rate):
    #    self._maxDownloadRate = int(rate)
    def getUploadLimit(self):
        return self._maxUploadRate

    def getDownloadRate(self):
        return self._downloadRate
    
    def getAverageDownloadRate(self):
        return self._averageDownloadRate
       
    #We upload data if we do not chock and the peer is interested 
    def getUploadRate(self):
        if( (self.chocking == False) and  (self.remoteConnection.interested == True) ):
            return self._uploadRate
        else:
            return 0

    def unchock(self, uploadRate=-1):
        if(uploadRate > -1):
            self._maxUploadRate = int(uploadRate)
        #if(downloadRate > -1):
        #    self._maxDownloadRate = int(downloadRate)
        self.chocking = False
        Log.pLD(self._srcPeer, "unchocking [{0}@{1}]".format(self._destPeer.pid, self._maxUploadRate) )
        self.__calculateUploadRate()
        self._freshUnchock = True
        #self._averageDownloadRate = 0

    
    #Is called at the beginning of every tick and calculates the upload bandwidth for this tick for this connection
    def updateLocalState(self, finishedPieces):
        self.finishedPieces = finishedPieces
        self.__calculateUploadRate()
        #self.__calculateDownloadRate()

    #Have a simple up to 10% distortion rate
    def __calculateUploadRate(self):
        self._uploadRate = self._maxUploadRate * ( 1.0 - ( random.random() % 0.1 ))
        self._uploadRate = int(self._uploadRate)

    #def __calculateDownloadRate(self):
    #    self._downloadRate = self._maxDownloadRate * ( 1.0 - ( random.random() % 0.1 ))
    #    self._downloadRate = int(self._downloadRate)

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
            self._srcPeer.peerDisconnect(self)
            return

        #Check if we are seeding , if so, we are __NEVER__ interested
        if(self._srcPeer.getTorrent().isFinished() == False):
        
            #Check what the other peer has to offer
            self._downloadablePieces = self.__calcDownloadablePieceSet()        
            if(len(self._downloadablePieces) > 0):
                Log.pLD(self._srcPeer, "Having interest in {0} from {1}".format( len(self._downloadablePieces), self._destPeer.pid) )
                self.interested = True
                self.__setCurrentPiece()
                #if( self.chocking == True ):
                #    self.unchock(self._uploadRate, 0)
            else:
                Log.pLD(self._srcPeer, "Loosing interest in peer {0}".format(self._destPeer.pid) )
                #self.chocking = True
                self.interested = False
        else:
            self.interested = False
        
    def runDownload(self):
        #If nothing happens, nothing is downloaded
        self._downloadRate = 0
        
        #Downloading happens if we are interested and the other peer is not chocking us
        if( (self.interested == True) and (self.remoteConnection.chocking == False) ):

            #Limit maximum download rate
            currentDownloadRate = self.remoteConnection.getUploadRate()
            currentDownloadRate = self._srcPeer.requestDownloadBandwidth(currentDownloadRate)
            #if(currentDownloadRate > self._maxDownloadRate):
            #    currentDownloadRate = self._maxDownloadRate

            #Check if we finished a complete piece and if so mark it as finished and get the next one
            self._acumulatedData += currentDownloadRate
           
            self._downloadRate = currentDownloadRate
            
            #Make this int so we dont get too long floating number in output log
            self._downloadRate = int(self._downloadRate)
            
            Log.pLD(self._srcPeer, "Downloaded {0}/{1} of piece {2}".format(self._acumulatedData, self._srcPeer.getTorrent().pieceSizeBytes, self._currentPiece) )
            while(self._acumulatedData > self._srcPeer.getTorrent().pieceSizeBytes):
                Log.pLD(self._srcPeer, "Finished downloading piece {0}".format(self._currentPiece) )
            
                self._srcPeer.finishedDownloadingPiece(self, self._currentPiece )
                self._acumulatedData -= self._srcPeer.getTorrent().pieceSizeBytes
                self._currentPiece = -1
                #Set a next piece and utilize the data downloaded for this one. If there are no more pieces discard the downloaded data
                if(self.__setCurrentPiece() == False):
                    self._acumulatedData = 0   #This is simulating lost bandwidth due to running out of piece requests
                    Log.pLD(self._srcPeer, "Piece request queue empty!" )
                    #On start of next round we will loose interest
                    #self.interested = False
            
            if(self._currentPiece == -1):
                self.__setCurrentPiece()

        #Remote peer lost interest in us, stop sending data
        #if( self.chocking == False and self.remoteConnection.interested == False ):
        #    Log.pLD(self._srcPeer, "Remote peer [{0}] lost interest, Chock!".format(self._destPeer.pid) )
        #    self.chock()
                    
        #if( self.remoteConnection.chocking == True):
        #    self._downloadRate = 0
        #    pass

    def postDownloadState(self):
        self._uploadRate = self.remoteConnection.getDownloadRate() #Should be the real upload consumption
        
        #If the other peer was able to download this round, rate your download rate
        #if( (self.interested == True) and (self.remoteConnection.chocking == False) ):
        #If we unchock and this either a TFT or an OU Slot than take notice of our average download Rate 
        #if( (self.chocking == False) and ( (self._srcPeer._peersConn[self._destPeer.pid][4] == 1) or (self._srcPeer._peersConn[self._destPeer.pid][4] == 2) ) ):
        #if( (self.chocking == False) and  (self.remoteConnection.interested == True) ):
        #    self._averageDownloadRate = int( ( self._downloadRate + self._averageDownloadRate ) / 2 )
        self._averageDownloadRate = int( (self._downloadRate + self._lastDownloadRate)/2.0 )
        self._lastDownloadRate = self._downloadRate
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
        self._downloadablePieces = self.__calcDownloadablePieceSet()

        if( len(self._downloadablePieces) == 0):
            return False
        if( self._currentPiece != -1):
            #Check if this piece is still available, if not choose a new one
            if self._currentPiece in self._downloadablePieces:
                #Log.pLD(self._srcPeer,"Still want piece {0} to from {1}".format(self._currentPiece, self._destPeer.pid) )
                return True #We already have a piece selected
    
        #shuffle the download list -> so we dont download the same piece from all peers
        #self._currentPiece = random.sample(self._downloadablePieces, 1)[0]
        #NO! dont shuffle, this is already done in the Peer.pieceSelection get them by order
        
        self._currentPiece = -1
        #Now find the first piece in the download Queue we could get from the remote peer
        for i in self._srcPeer.piecesQueue:
            if( i in self._downloadablePieces):
                self._currentPiece = i
                break
        
        if(self._currentPiece != -1):
            #Remove the selected piece from the queue to reduce the chance of double piece download. Remember that it will be added again into the Queue
            #(that is ok )if Its not marked as downloaded at the next pieceSelection call in Peer 
            self._srcPeer.downloadingPiece(self._currentPiece)
        
            #Log.pLD(self._srcPeer,"Selecting piece {0} to get from {1}".format(self._currentPiece, self._destPeer.pid) )
            return True
        else:
            return False #Nothing to download
    
    def __calcDownloadablePieceSet(self):
        return self._srcPeer._torrent.getEmptyPieces() & self.remoteConnection.finishedPieces   


