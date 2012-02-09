'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''

import logging.config
from simulation.SSimulator import SSimulator

class Log(object):

    WARN = 13
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    ERROR = logging.ERROR


    def __init__(self):
        logging.config.fileConfig("log.conf")
        logging.addLevelName(self.WARN, "WARN")
            
    #Peer Logging Info
    def pLI(peer, msg):
        Log.peerLogging(peer.pid, Log.INFO, msg)
    
    #Peer Logging Debug
    def pLD(peer, msg):
        Log.peerLogging(peer.pid, Log.DEBUG, msg)
        
    #Peer Logging Warn
    def pLW(peer, msg):
        Log.peerLogging(peer.pid, Log.WARN, msg)
    
    #Peer Logging Error
    def pLE(peer, msg):
        Log.peerLogging(peer.pid, Log.ERROR, msg)
        
    def peerLogging(pID, level, msg):
        logging.log(level, "{0}:{1}  [{2}] {3}".format( SSimulator().tick, SSimulator().stage, pID, msg ))

    #write to log
    def w(level,msg):
        logging.log( level, msg )

    pLI = staticmethod(pLI)
    pLD = staticmethod(pLD)
    pLW = staticmethod(pLW)
    pLE = staticmethod(pLE)
    peerLogging = staticmethod(peerLogging)
    w = staticmethod(w)
        
