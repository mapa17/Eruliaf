'''
Created on Mar 26, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''

from simulation.Configuration import Configuration

class SConfig(object):
    _singelton = None
    _path = "default.cfg"
    
    def __new__(cls, *args, **kwargs):
        if( cls._singelton == None ):
            cls._singelton = Configuration(SConfig._path)
        return cls._singelton

    @staticmethod
    def setPath(path):
        SConfig._path = path
        