'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''

import logging
#from utils.Log import Log
import queue
import threading
#from simulation.SimElement import SimElement

class SimulationThread( threading.Thread ):
    def __init__(self, eventQueue, simulador ):
        threading.Thread.__init__(self)
        self.eventQueue = eventQueue
        self.simulador = simulador

    def run(self):
        while(True):
            e = self.eventQueue.get()
            if( isinstance(e, int ) ):
                #print("Closing thread ...")
                self.eventQueue.task_done()
                return
            else:
                e.nextTick(self.simulador.tick, self.simulador.stage)
                self.eventQueue.task_done()


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
        self._multithreading = False #Turn off multithreading by default!

        self.simQueue = queue.Queue()
        self._threads = []
        self._numberOfThreads = 4
        
        for i in range( 0, self._numberOfThreads):
            self._threads.append( SimulationThread(self.simQueue, self) )

        for t in self._threads:
            t.start()

    def addSimulationElement(self, element):
        self.__elements.append(element)

    def delSimulationElement(self, element):
        self.__elements.remove(element)

    def simTick(self):
        self.tick+=1
        
        if self._multithreading == True : 
            for s in Simulator._stage :
                self.stage = s
                for e in self.__elements :
                    #self.simQueue.put_nowait(e)
                    self.simQueue.put(e)

                self.simQueue.join()
        else:
            for s in Simulator._stage :
                self.stage = s
                for e in self.__elements :
                    e.nextTick(self.tick, s)
        
    def endSimulation(self):
        #Send all threads a zero (integer) so that they will terminate
        for i in self._threads:
            self.simQueue.put( 0 )
        
        self.simQueue.join()

    def testSimEnd(self):
        if(self.tick == 500):
            logging.log(logging.INFO, "Time to end the simulation ...")
            return True
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

        self.endSimulation()


