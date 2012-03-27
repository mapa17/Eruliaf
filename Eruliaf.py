'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''
import sys
from simulation.SSimulator import SSimulator
from nodes.Peer import Peer
from nodes.Seeder import Seeder
from nodes.Tracker import Tracker
from utils.Torrent import Torrent
from utils.Log import Log
import logging
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
    
    #print("Stats fiel from config {0}".format(SConfig().value("logCfg") ))
    #sys.exit(0)
    newLog = Log() #Create this log for the whole project
    logging.log(Log.INFO, "Starting simulation")
    
    S = SSimulator()
    T = Tracker()
    O = Observer( T )    
    
    logging.log(Log.INFO, "Creating nodes ...")
    
    tor = Torrent( SConfig().value("TorrentSize") , T)
    Log.w(Log.INFO, "Piece size [{0}] bytes".format(tor.pieceSizeBytes) )
    s = Seeder( tor , SConfig().value("SeederUpload"), SConfig().value("SeederDownload") )
    
    logging.log(Log.INFO, "Creating {0}".format(s))
    #logging.log(Log.INFO, "Creating {0}".format(p1))
    
    T.addPeer(s)
    #T.addPeer(p1)
    
    pF = PeerFactory(T)

    S.start()

    logging.log(Log.INFO, "Ending simulation")    
    
