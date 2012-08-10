'''
Created on Feb 2, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es

    Copyright (C) 2012  Pasieka Manuel , mapa17@posgrado.upv.es

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
from simulation.SSimulator import SSimulator

class SimElement(object):

    def __init__(self):
        SSimulator().addSimulationElement(self)
        self.__simFunctions = []

    def __str__(self, *args, **kwargs):
        return "Simulation Element"
    
    def nextTick(self, tick, stage):
        #print("{2} running tick [{0} : {1}]".format(tick, stage, self ) )
        
        # self.__simFunctions is holding a list of tuples the kind ( #stage , Function )
        # Iterate through all registered function and execute all for this stage
        
        for i in self.__simFunctions :
            if( (i[0]) == stage ):
                i[1]()

    def registerSimFunction(self, stage, function):
        self.__simFunctions.append( (stage, function) )

    def unregisterSimFunction(self, stage, function):
        if( (stage, function) in self.__simFunctions ):
            self.__simFunctions.remove( (stage, function) )

    def removeSimElement(self):
        SSimulator().delSimulationElement(self)
        
