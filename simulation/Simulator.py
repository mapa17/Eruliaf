'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''

class Simulator(object):
    '''
    classdocs
    '''

    _singelton = None
    _initialized = False
    _stage = [0,1,2,3]
    
#    def __new__(cls, *args, **kwargs):
#        if( cls._singelton == None ):
#        #if not cls._singelton :
#            cls._singelton = super(Simulator, cls).__new__(cls, *args, **kwargs)
#            cls._initialized = True
#        return cls._singelton


    def __init__(self):
        #if(self._initialized == False):
        print("New Simulator!")
        self.__tick = -1
        self.__elements = []
        self.__nodeId = -1
        self.__peerId = -1

    def addSimulationElement(self, element):
        self.__elements.append(element)
        
    def getTick(self):
        return self.__tick;
    
    def simTick(self):
        self.__tick+=1
        
        for s in Simulator._stage :
            for e in self.__elements :
                e.nextTick(self.__tick, s)
                
        #TODO: simulate tick

    def testSimEnd(self):
        if(self.getTick() == 2):
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
        while (self.testSimEnd() == False) :
            self.simTick()