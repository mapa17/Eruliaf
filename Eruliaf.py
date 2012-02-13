'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''
from simulation.SSimulator import SSimulator
from nodes.Peer import Peer
from nodes.Seeder import Seeder
from nodes.Tracker import Tracker
from utils.Torrent import Torrent
from utils.Log import Log
import logging
from simulation.PeerFactory import PeerFactory

if __name__ == '__main__':
    
    newLog = Log() #Create this log for the whole project
    logging.log(Log.INFO, "Starting simulation")
    
    S = SSimulator()
    T = Tracker()
    
    logging.log(Log.INFO, "Creating nodes ...")
    
    s = Seeder( Torrent(1024*1024*1, T) , 1024*20, 1024*10)
    
    logging.log(Log.INFO, "Creating {0}".format(s))
    #logging.log(Log.INFO, "Creating {0}".format(p1))
    
    T.addPeer(s)
    #T.addPeer(p1)
    
    pF = PeerFactory(T)

    S.start()

    logging.log(Log.INFO, "Ending simulation")    
    
