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
from simulation.SimElement import SimElement
from simulation.SSimulator import SSimulator

class Node(SimElement):

    nid = -1 

    def __init__(self):
        super().__init__()
        self.nid = SSimulator().getNewNodeId()
        
    def __str__(self, *args, **kwargs):
        return "Node (0)".format(self.nid)
    
    def getNodeId(self):
        return self.nid
        