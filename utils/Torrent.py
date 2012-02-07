'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''

class Torrent(object):

    __blockSize = 512 #Size in bytes
    __nPieces = 500 #Number of pieces per torrent is fixed, what is variable is the number of blocks per piece
#    __pieceSize = calculated in __init__() ... number of blocks per piece

    __Cempty = 0
    __Cdownloading = 1
    __Cfinished = 2
    tracker = None
    

    #Create torrent bitMap File
    #size ... in Bytes
    def __init__(self, size, tracker):
        self.pieceSizeBytes = size/self.__nPieces
        self.pieceSize = self.pieceSizeBytes/self.__blockSize
        self.__pieces = [ self.__Cempty ] * self.__nPieces #Initialize the piece list
        self.__nFinishedPieces = 0
        self.__finishedTorrent = False
        self.tracker = tracker
    
    def getFinishedPieces(self):
        return set( self.getPieceSubSet(self.__Cfinished, self.__nFinishedPieces) ) #set of piece indexes
        
    def getDownloadingPieces(self, n):
        return set( self.getPieceSubSet(self.__Cdownloading, n) ) #Set of piece indexes
    
    def getEmptyPieces(self, n):
        return set( self.getPieceSubSet(self.__Cempty, n) ) #Set of piece indexes
        
    def getNumberOfPieces(self):
        return self.__nPieces
        
    def getNumberOfFinishedPieces(self):
        return self.__nFinishedPieces
        
    def getNumberOfNotFinishedPieces(self):
        return self.__nPieces - self.__nFinishedPieces #This are empty AND downloading pieces
        
        '''
            Returns a set of the indexes of the pieces in the specified state
        '''
    def getPieceSubSet(self, state, n):
        subSet = []
        
        for i,d in enumerate(self.__pieces) :
            
            if(len(subSet) == n):
                break
                
            if( d == state ) :
                subSet.append(i)
                
        return subSet
    
    def setFinished(self):
        self.__finishedTorrent = True
        self.__nFinishedPieces = self.__nPieces
        self.__pieces = [ self.__Cfinished ] * self.__nPieces #Set all to finished
    
    def isFinished(self):
        return self.__finishedTorrent
                
    def getBlockSize(self):
        return self.__blockSize
    
    def downloadPiece(self, piece):
        if(piece >= 0 and piece < len(self.__pieces) and self.__pieces[piece] == self.__Cempty) :
            self.__pieces[piece] = self.__Cdownloading
            
    def finishedPiece(self, piece):
        if(piece >= 0 and piece < len(self.__pieces) and self.__pieces[piece] != self.__Cfinished) :
            self.__pieces[piece] = self.__Cfinished
            self.__nFinishedPieces+=1
            if(self.__nFinishedPieces == self.__nPieces) :
                self.__finishedTorrent = True
            
    def setEmptyPiece(self, piece):
        if(piece >= 0 and piece < len(self.__pieces) ) :
            self.__pieces[piece] = self.__Cempty
    