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