'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''

import configparser

class Configuration(object):

    def __init__(self, path):
        
        self._config = configparser.SafeConfigParser()
        self._config.readfp(open(path))
        #self._config.read(path)

        print("Loading config file {0}".format(path))
        
        #self.cfgValue = {}
    
    def value(self, key, section="General"):
        return self._config.get(section, key) 