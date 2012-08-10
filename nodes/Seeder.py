'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es

    Copyright (C) 2012  Pasieka Manuel , mapa17@posgrado.upv.es

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
from nodes.Peer import Peer

class Seeder(Peer):

    def __init__(self, torrent, uploadRate, downloadRate):
        torrent.setFinished(False)
        super().__init__(torrent, uploadRate, downloadRate, 0) #Seeder does not sleep
        
        self._isSeeder = True
        self._SuperSeedingSize = 20
        self.__SuperSeedingPieceSet = set()
        self.topPiece = 0
        self.changeSeedingSet()
        
        #Seeder should know more peers
        self._maxPeerListSize = 100

        
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
            self._torrent.setFinished()
            return

        newTop = self.topPiece + self._SuperSeedingSize
        if( newTop > nPieces ):
            newTop = nPieces

        self.__SuperSeedingPieceSet = set( list( x for x in range(self.topPiece, newTop) ) )
        self.topPiece = newTop
        
        for i in self.__SuperSeedingPieceSet :
            self._torrent.finishedPiece(i)

