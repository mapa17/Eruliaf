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
        self._maxDownloadRate = 0
        self._maxUploadRate = 0
        
        self.chocking = True
        self.interested = False
        self.disconnected = False

        self.finishedPieces = set()
        
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

    def setDownloadLimit(self, rate):
        self._maxDownloadRate = int(rate)

    def getDownloadRate(self):
        return self.__downloadRate
        
    def getUploadRate(self):
        if( self.__uploadRate > self.remoteConnection.getDownloadRate() ):
            self.__uploadRate = self.remoteConnection.getDownloadRate() 
        return self.__uploadRate

    def unchock(self, uploadRate=-1, downloadRate=-1):
        if(uploadRate > -1):
            self._maxUploadRate = int(uploadRate)
        if(downloadRate > -1):
            self._maxDownloadRate = int(downloadRate)
        self.chocking = False
        Log.pLD(self.__srcPeer, "unchocking [{0}@{1}/{2}]".format(self.__destPeer.pid, self._maxUploadRate, self._maxDownloadRate) )

    '''
    #Is called from remoteConnection when it unchocks this peer
    def unchockRemote(self):
        self.__srcPeer.unchockHappend()
    '''

    '''
        This is called with stage 0 on every tick and has the following tasks:
            # Update interest and chock status for this connection
            # If a active download is going on, check for piece completion and assign new piece to download
    '''
    def updateLocalState(self, finishedPieces):
        self.finishedPieces = finishedPieces
        self.__calculateUploadRate()
        self.__calculateDownloadRate()

    #Have a simple up to 10% distortion rate
    def __calculateUploadRate(self):
        self.__uploadRate = self._maxUploadRate * ( 1.0 - ( random.random() % 0.1 ))
        self.__uploadRate = int(self.__uploadRate)

    def __calculateDownloadRate(self):
        self.__downloadRate = self._maxDownloadRate * ( 1.0 - ( random.random() % 0.1 ))
        self.__downloadRate = int(self.__downloadRate)

    def peerIsInterested(self):
        try:
            return self.remoteConnection.interested
        except:
            pass

    def peerIsChocking(self):
        return self.remoteConnection.chocking

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
        
        #Downloading happens if we are interested and the other peer is not chocking us
        if( self.interested == True and self.remoteConnection.chocking == False):

            #Limit maximum download rate
            currentDownloadRate = self.remoteConnection.getUploadRate()
            if(currentDownloadRate > self._maxDownloadRate):
                currentDownloadRate = self._maxDownloadRate

            #Check if we finished a complete piece and if so mark it as finished and get the next one
            self.__acumulatedData += currentDownloadRate
           
            if(self.__downloadRate == 0):
                self.__downloadRate = currentDownloadRate
            else:
                self.__downloadRate = ( self.__downloadRate + currentDownloadRate ) / 2
            
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
                    self.interested = False
            
            if(self.__currentPiece == -1):
                self.__setCurrentPiece()

        #Remote peer lost interest in us, stop sending data
        if( self.chocking == False and self.remoteConnection.interested == False ):
            Log.pLD(self.__srcPeer, "Remote peer [{0}] lost interest, Chock!".format(self.__destPeer.pid) )
            self.chock()
                    
        if( self.remoteConnection.chocking == True):
            #self.__downloadRate = 0
            pass

    #Select a piece for downloading
    def __setCurrentPiece(self):
        self.__calcDownloadablePieceSet()

        if( len(self.__downloadablePieces) == 0):
            return False
        if( self.__currentPiece != -1):
            #Check if this piece is still available, if not choose a new one
            if self.__currentPiece in self.__downloadablePieces:
                Log.pLD(self.__srcPeer,"Still want piece {0} to from {1}".format(self.__currentPiece, self.__destPeer.pid) )
                return True #We allready have a piece slected
    
        #shuffle the download list -> so we dont download the same piece from all peers
        self.__currentPiece = random.sample(self.__downloadablePieces, 1)[0]
        Log.pLD(self.__srcPeer,"Selecting piece {0} to get from {1}".format(self.__currentPiece, self.__destPeer.pid) )
        return True
    
    def __calcDownloadablePieceSet(self):
        self.__downloadablePieces = self.__srcPeer.piecesQueue & self.remoteConnection.finishedPieces   


