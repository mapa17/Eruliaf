'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''

from simulation.SSimulator import SSimulator
from utils.Log import Log
from simulation.SConfig import SConfig

#We only simulate the exchange of pieces, there are no blocks.
#There for we have the problem that if the piece size gets too big, nodes will take a lot longer
#than one TFT slot period to download a single piece!!!
#To prevent this make the piece size an scenario argument and than calculate the nPieces accordingly!

class Torrent(object):
    __nPieces = -1 #Number of pieces per torrent is fixed, what is variable is the number of blocks per piece

    __Cempty = 0
    __Cdownloading = 1
    __Cfinished = 2
    tracker = None
    

    #Create torrent bitMap File
    #size ... in Bytes
    def __init__(self, tracker):
        
        self.pieceSizeBytes= int( SConfig().value("PieceSize") )
        self.torrentSize = int( SConfig().value("TorrentSize") )
        self.__nPieces = int( self.torrentSize / self.pieceSizeBytes )  
        self.__pieces = [ self.__Cempty ] * self.__nPieces #Initialize the piece list
        self.__nFinishedPieces = 0
        self.__finishedTorrent = False
        self.tracker = tracker
        self._finishTick = -1 #Time the torrent finished download

        
    def getFinishedPieces(self):
        return set( self.getPieceSubSet(self.__Cfinished, self.__nFinishedPieces) ) #set of piece indexes
        
    #def getDownloadingPieces(self, n):
    #    return set( self.getPieceSubSet(self.__Cdownloading, n) ) #Set of piece indexes
    
    def getEmptyPieces(self, n):
        return set( self.getPieceSubSet(self.__Cempty, n) ) #Set of piece indexes
        
    def getNumberOfPieces(self):
        return self.__nPieces
        
    def getNumberOfFinishedPieces(self):
        return self.__nFinishedPieces

    #def getNumberOfDownloadingPieces(self):
    #    dl = self.getDownloadingPieces(self.__nPieces)
    #    return len( dl )

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
    
    def setFinished(self, flagPieces = True):
        self.__finishedTorrent = True
        self._finishTick = SSimulator().tick
        if( flagPieces ):
            self.__nFinishedPieces = self.__nPieces
            self.__pieces = [ self.__Cfinished ] * self.__nPieces #Set all to finished
    
    def isFinished(self):
        return self.__finishedTorrent
                
    def getBlockSize(self):
        return self.__blockSize
    
    #def downloadPiece(self, piece):
    #    if(piece >= 0 and piece < len(self.__pieces) and self.__pieces[piece] == self.__Cempty) :
    #        self.__pieces[piece] = self.__Cdownloading
            
    def finishedPiece(self, piece):
        if( self.__pieces[piece] == self.__Cfinished):
            print("double donwload of piece {0}!".format(piece) )
        if(piece >= 0 and piece < len(self.__pieces) and self.__pieces[piece] != self.__Cfinished) :
            self.__pieces[piece] = self.__Cfinished
            self.__nFinishedPieces+=1
            if(self.__nFinishedPieces == self.__nPieces) :
                self.setFinished(False) 

    def setEmptyPiece(self, piece):
        if(piece >= 0 and piece < len(self.__pieces) ) :
            self.__pieces[piece] = self.__Cempty
    
