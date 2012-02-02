'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''
from simulation.SSimulator import SSimulator
from simulation.SimElement import SimElement
from nodes.Node import Node
from nodes.Peer import Peer
from nodes.Seeder import Seeder
from nodes.Tracker import Tracker

if __name__ == '__main__':
    S = SSimulator()
    print(S)
    e1 = SimElement()
    #e2 = SimElement()
    e2 = Node()
    e3 = Peer()
    e4 = Seeder()
    e5 = Tracker()
    
    S2 = SSimulator()
    print(S2)
    
    S.start()
    
    print("Ending simulation ...")
    pass