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
        self._emptyPieces = set(range(self.__nPieces))
        self._completedPieces = set()
        self._nFinishedPieces = 0
        self.__finishedTorrent = False
        self.tracker = tracker
        self._finishTick = -1 #Time the torrent finished download

    
    #Returns a set of the piece number of all completed pieces
    def getFinishedPieces(self):
        return self._completedPieces
    
    def getEmptyPieces(self):
        return self._emptyPieces
        
    def getNumberOfPieces(self):
        return self.__nPieces
        
    def getNumberOfFinishedPieces(self):
        return self._nFinishedPieces

    #def getNumberOfDownloadingPieces(self):
    #    dl = self.getDownloadingPieces(self.__nPieces)
    #    return len( dl )

    def getNumberOfNotFinishedPieces(self):
        return self.__nPieces - self._nFinishedPieces #This are empty AND downloading pieces
        
    def setFinished(self, flagPieces = True):
        self.__finishedTorrent = True
        self._finishTick = SSimulator().tick
        if( flagPieces ):
            self._nFinishedPieces = self.__nPieces
            self._completedPieces = set( range(self.__nPieces) )
    
    def isFinished(self):
        return self.__finishedTorrent
                
    #def downloadPiece(self, piece):
    #    if(piece >= 0 and piece < len(self.__pieces) and self.__pieces[piece] == self.__Cempty) :
    #        self.__pieces[piece] = self.__Cdownloading
            
    def finishedPiece(self, piece):
        if( piece in self._completedPieces ):
            Log.w(Log.WARN, "double donwload of piece {0}!".format(piece))
        elif( piece >= 0 and piece < self.__nPieces ) :
            self._emptyPieces.remove(piece)
            self._completedPieces.add(piece)
            self._nFinishedPieces += 1
            if(self._nFinishedPieces == self.__nPieces) :
                self.setFinished(False) 

    def setEmptyPiece(self, piece):
        if(piece >= 0 and piece < self.__nPieces ) :
            if( piece in self._completedPieces):
                self._completedPieces.remove(piece)
            self._emptyPieces.add(piece)
    
