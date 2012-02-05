'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''
from simulation.SSimulator import SSimulator
from nodes.Peer import Peer
from nodes.Seeder import Seeder
from nodes.Tracker import Tracker
from utils.Torrent import Torrent

if __name__ == '__main__':
    S = SSimulator()
    T = Tracker()
    
    print("Init nodes ...")
    
    tor = Torrent(1024*1024*10, T)
    tor.setFinished()
    s = Seeder( tor )
    p1 = Peer( Torrent(1024*1024*10, T) )
    
    print(s)
    print(p1)
    
    T.addPeer(s)
    T.addPeer(p1)
    
    S.start()
    
    print("Ending simulation ...")
