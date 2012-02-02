'''
Created on Feb 2, 2012

@author: dd
'''
from simulation.Simulator import Simulator

'''
Wrapper class around simulation.Simulator which implements the
singelton pattern.
'''

class SSimulator(object):
    _singelton = None

    def __new__(cls, *args, **kwargs):
        if( cls._singelton == None ):
        #if not cls._singelton :
            cls._singelton = Simulator()
        return cls._singelton

#    def __init__(self):
#        print("Get Simulator Ref...")        