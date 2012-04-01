'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''

import logging.config
from simulation.SSimulator import SSimulator
from simulation.SConfig import SConfig
import os

class Log(object):

    WARN = 13 #Make it compatible with java log
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    ERROR = logging.ERROR


    def __init__(self):
        #path = SConfig().value("logCfg")
        logFile = str(SConfig().value("logFile"))
        logLevel = str(SConfig().value("logLevel"))
        print("Creating logfile {0} with logLevel = {1}".format( logFile, logLevel) )
        
        logging.basicConfig(filename=logFile,
                            filemode='w',
                            format='%(filename)s %(levelname)s - %(message)s',
                            level=logLevel)

        
        #logging.config.fileConfig( path )
        #logging.config.fileConfig( "./log.conf" )
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
        
