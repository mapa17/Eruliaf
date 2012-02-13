'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''

import logging
#from utils.Log import Log

class Simulator(object):
    _singelton = None
    _initialized = False
    _stage = [0,1,2,3,4]

    #Simulation stages
    ST_INIT = 0
    ST_UPDATE_LOCAL = 1
    ST_UPDATE_GLOBAL = 2
    ST_LOGIC = 3
    ST_STATIS = 4

    def __init__(self):        
        logging.log(logging.INFO, "Creating Simulator ...")
        self.tick = -1
        self.stage = -1
        self.__elements = []
        self.__nodeId = -1
        self.__peerId = -1

    def addSimulationElement(self, element):
        self.__elements.append(element)

    def delSimulationElement(self, element):
        self.__elements.remove(element)

    def simTick(self):
        self.tick+=1
        
        for s in Simulator._stage :
            self.stage = s
            for e in self.__elements :
                e.nextTick(self.tick, s)

    def testSimEnd(self):
        if(self.tick == 500):
            return True
            logging.log(logging.INFO, "Time to end the simulation ...")
        else:
            return False

    def getNewNodeId(self):
        self.__nodeId+=1
        return self.__nodeId
    
    def getNewPeerId(self):
        self.__peerId+=1
        return self.__peerId
        

#Start Simulation
    def start(self):
        logging.log(logging.INFO, "Starting simulation ...")
        while (self.testSimEnd() == False) :
            self.simTick()
