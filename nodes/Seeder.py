'''
Created on Feb 2, 2012

@author: dd
'''
from nodes.Peer import Peer

class Seeder(Peer):

    def __init__(self):
        Peer.__init__(self)
        
    def __str__(self, *args, **kwargs):
        return "Seeder"