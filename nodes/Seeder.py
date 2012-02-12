'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''
from nodes.Peer import Peer

class Seeder(Peer):

    def __init__(self, torrent):
        torrent.setFinished(False)
        super().__init__(torrent)
        
        self._isSeeder = True
        self._SuperSeedingSize = 20
        self.__SuperSeedingPieceSet = set()
        self.topPiece = 0
        self.changeSeedingSet()

        
    def __str__(self, *args, **kwargs):
        return "Seeder [pid {0}, nid {1} ]".format(self.pid, self.nid)

    #Implement Super Seeding by pretending to always only have one piece of the torrent 
    #For that iterate through all pieces of the torrent, and start seeding the next if at least
    #one peer has finished this piece. If once iterated through all pieces, stop superseeding
    #and seed normally
    def updateLocalConnectionState(self):
         
        if( len(self.__SuperSeedingPieceSet) != 0):
            for i in self._peersConn.values() : 
                if self.__SuperSeedingPieceSet.issubset(i[2].remoteConnection.finishedPieces) :
                    self.changeSeedingSet()             
        
        super().updateLocalConnectionState()

    def changeSeedingSet(self) :
        nPieces = self._torrent.getNumberOfPieces()

        if( len(self.__SuperSeedingPieceSet) != 0):
            for i in self.__SuperSeedingPieceSet:
                self._torrent.setEmptyPiece(i)

        #If we have already seeded the last piece, clear set
        if( self.topPiece ==  nPieces ):
            self.__SuperSeedingPieceSet = set()
            return

        newTop = self.topPiece + self._SuperSeedingSize
        if( newTop > nPieces ):
            newTop = nPieces

        self.__SuperSeedingPieceSet = set( list( x for x in range(self.topPiece, newTop) ) )
        self.topPiece = newTop
        
        for i in self.__SuperSeedingPieceSet :
            self._torrent.finishedPiece(i)

