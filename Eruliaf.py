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
import sys
from simulation.SSimulator import SSimulator
from nodes.Peer import Peer
from nodes.Seeder import Seeder
from nodes.Tracker import Tracker
from utils.Torrent import Torrent
from utils.Log import Log
import logging
import random
from simulation.PeerFactory import PeerFactory
from simulation.Observer import Observer
from simulation.SConfig import SConfig

def getUsage(progName):
    return "{0} [CONFIG_FILE]".format(progName)

if __name__ == '__main__':
    
    if( len(sys.argv) < 2):
        print("Usage: {0}".format(getUsage(sys.argv[0])))
        sys.exit(1)
        
    #Load Config
    SConfig.setPath( sys.argv[1] )
    C = SConfig()
    
    print("Starting Simulation with config {0}".format(sys.argv[1] ))
    #import time
    #time.sleep(5)
    random.seed(int(SConfig().value("randSeed")))
    newLog = Log() #Create this log for the whole project
    logging.log(Log.INFO, "Starting simulation") 
    
    S = SSimulator()
    T = Tracker()
    O = Observer( T )    
    
    logging.log(Log.INFO, "Creating nodes ...")
        
    tor = Torrent( T )
    Log.w(Log.INFO, "Piece size [{0}] bytes".format(tor.pieceSizeBytes) )
    s = Seeder( tor , SConfig().value("SeederUpload"), SConfig().value("SeederDownload") )
    
    logging.log(Log.INFO, "Creating {0}".format(s))
    
    pF = PeerFactory(T)

    S.start()

    logging.log(Log.INFO, "Ending simulation")    
    
    sys.exit(0)
