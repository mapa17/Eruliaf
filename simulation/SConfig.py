'''
Created on Mar 26, 2012

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
        