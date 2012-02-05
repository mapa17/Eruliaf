'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''
from random import random

class Connection(object):
    
    __srcPeer = None
    __destPeer = None
    
    def __init__(self, src, dest):
        self.__srcPeer = src
        self.__destPeer = dest
        self.__uploadRate = 0
        self.__downloadRate = 0
        
        self.chocking = False
        self.interested = False
        #self.__peerChocking = 1
        #self.__peerInterested = 0
        
        self.finishedPieces = set()
        self.interestingPieces = set()
        
        self.__acumulatedData = 0
        self.finishedPieces = set()
        self.interestingPieces = set()
        self.__nextPieces = set()
        self.__currentPiece = -1
    
    def connect(self):
        #This is the connection element on the other side
        self.__remoteConnection =  self.__destPeer.connectToPeer(self.__srcPeer)
    
    def transferData(self, uploadRate):
        print("Transfer piece [{0}\@ {2}] -> [{1}]".format(self.__srcPeer.pid, self.__destPeer.pid, uploadRate) )
        self.chocking = False #Next update() call will select piece ( so first second is downloading but what is defined later. This simulates that the wanted pieces are already selected earlier
    
    '''
        This is called with stage 0 on every tick and has the following tasks:
            # Update interest and chock status for this connection
            # If a active download is going on, check for piece completion and assign new piece to download
    '''
    def update(self, finishedPieces, interestingPieces):
        self.finishedPieces = finishedPieces
        self.interestingPieces = interestingPieces
        
        #Check what the other peer has to offer
        self.__nextPieces = self.interestingPieces & self.__remoteConnection.finishedPieces
        if(len(self.__nextPieces) > 0):
            self.interested = True
        else:
            self.chocking = True
            self.interested = False
        
        self.__uploadRate = self.__uploadRate # dont modify this right now, later simulate fluctuation
        
        if( self.chocking == False and self.__remoteConnection.chocking == False):
        
            #shuffle the download list -> so we dont download the same piece from all peers
            self.__nextPieces = random.sample(self.__nextPieces, len(self.__nextPieces))
        
            #Check if we finished a complete piece and if so mark it as finished and get the next one
            self.__downloadRate = self.__remoteConnection.getUploadRate()
            self.__acumulatedData += self.__downloadRate
            if(self.__acumulatedData > self.__srcPeer.getTorrent().pieceSizeBytes):
                print("[{0}] Finished downloading piece {1}".format(self.__srcPeer.pid, self.__currentPiece) )
                self.__srcPeer.getTorrent().finishedPiece( self.__currentPiece )
                self.__acumulatedData = 0
                self.__currentPiece = -1
            
            if(self.__currentPiece == -1):
                self.__currentPiece = self.__nextPieces.pop()
                self.__srcPeer.getTorrent().downloadPiece(self.__currentPiece)
                print("[{0}] Selecting piece {1} to transfer to {2}".format(self.__srcPeer.pid, self.__currentPiece, self.__destPeer.pid) )
        else :
            #If for some reason we are not transferring data any more, halt everything and reset the download state of this piece
            print("[{0}] Download is stopped".format(self.__srcPeer.pid) )
            self.__downloadRate = 0
            if( self.__currentPiece != -1 ):
                self.__srcPeer.getTorrent().setEmptyPiece(self.__currentPiece)
                self.__currentPiece = -1
        
        
    def getDownloadRate(self):
        return self.__downloadRate
    
    def setUploadRate(self, rate):
        self.__uploadRate = rate
        
    #called from other connection
    def getUploadRate(self):
        return self.__uploadRate