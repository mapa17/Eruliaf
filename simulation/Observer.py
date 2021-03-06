'''
Created on Feb 16, 2012

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

from simulation.SSimulator import SSimulator
from simulation.Simulator import Simulator
from simulation.SimElement import SimElement
from nodes.Peer import Peer
from nodes.Peer_C1 import Peer_C1
from simulation.SConfig import SConfig

class Observer(SimElement):

    def __init__(self, tracker):
        super().__init__()
        
        self._peers = []
        self._tracker = tracker

        self.stats = SConfig().value("statsFile") # "./statistics/statistics.csv"
        
        self._createOutputFiles()

        self.registerSimFunction(Simulator.ST_STATISTICS, self.logic )
        self.registerSimFunction(Simulator.ST_SIMULATION_END, self._endSimulation )

    def logic(self):
        #Run for every peer
        self.t = SSimulator().tick
        for p in self._tracker._peers:
            
            if( p.__class__.__name__ == "Seeder" ):
                continue
            
            self._peerStatistics(p)
    
    
    #Prints statistics about the actual down/upload rate of each peer once every tick
    def _peerStatistics(self, peer):
        #Count number of peers and number of completed peers
        if( peer.__class__.__name__ == "Peer" ):
            name = "Peer"
           
        if( peer.__class__.__name__ == "Peer_C1" ):
            name = "Peer_C1"
            
        # Log format :
        #<Tick> <peer Type> <id> <downloadStart> <DownloadEnd>
        #<Max Upload Rate> <Max Download Rate> <Current Upload Rate> <Current Download Rate>
        #<Total # of max TFT Slots> <Total # of max OU Slots> <Total # of used TFT Slots> <Total # of used OU Slots>
        #<Total #Bytes TFT Download> <Total #Bytes TFT Upload> <Total #Bytes OU Download> <Total #Bytes OU Upload>
        #<# Downloaded pieces><# Total Pieces>
        #<# of connected Peers>

        #Write Stats to file
        fd = self._fd_statists
        fd.write("{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{}\n".format(self.t, name, peer.pid, peer._downloadStart, peer._downloadEnd, \
                    peer._maxUploadRate, peer._maxDownloadRate, peer._uploadRateLastTick, peer._downloadRateLastTick, \
                    peer._maxTFTSlots, peer._maxOUSlots, peer._nTFTSlots, peer._nOUSlots, \
                    peer._TFTByteDownload, peer._TFTByteUpload, peer._OUByteDownload, peer._OUByteUpload, \
                    peer._torrent.getNumberOfFinishedPieces(), peer._torrent.getNumberOfPieces() , \
                    len(peer._peersConn) ) )
        

    def _endSimulation(self):
        self._closeOutputFiles()

    def _createOutputFiles(self):

        formatDesc = "# Log format : <Tick> <peer Type> <id> <downloadStart> <DownloadEnd>\n#<Max Upload Rate> <Max Download Rate> <Current Upload Rate> <Current Download Rate> \n#<Total # of max TFT Slots> <Total # of max OU Slots> <Total # of used TFT Slots> <Total # of used OU Slots> \n#<#Bytes TFT Download> <#Bytes TFT Upload> <#Bytes OU Download> <#Bytes OU Upload>\n#<# Downloaded pieces><# Total Pieces>\n##<# of connected Peers>\n"
        self._fd_statists = open( self.stats, "w" )
        self._fd_statists.write(formatDesc)
            
    def _closeOutputFiles(self):
            
        self._fd_statists.close()