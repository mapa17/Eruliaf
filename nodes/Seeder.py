'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''
from nodes.Peer import Peer

class Seeder(Peer):

    def __init__(self, torrent):
        super().__init__(torrent)
        
    def __str__(self, *args, **kwargs):
        return "Seeder [pid {0}, nid {1} ]".format(self.pid, self.nid)