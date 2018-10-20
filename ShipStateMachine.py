#!/usr/bin/env python3
# Python 3.6

import hlt
from hlt import constants
from hlt.positionals import Direction
import random
import logging
import helperfunctions

from enum import Enum     # for enum34, or the stdlib version
# from aenum import Enum  # for the aenum version
ShipState = Enum('ShipState', 'north east south west returnHome harvest')

def StateMachine(CQueue, state):
  if state == ShipState.north:
  elif state == ShipState.east:
  elif state == ShipState.south:
  elif state == ShipState.west:
  elif state == ShipState.returnHome:
    ShipInfos[ship.id].ReturnHome = True
    MoveQueue = ShortestPath( ship.position, me.shipyard.position )
    if not MoveQueue:
      logging.info("Not returning home anymore")
      ShipInfos[ship.id].ReturnHome = False
    else:
      CQueue.append( ship.move( MoveQueue[0] ))
  elif state == ShipState.harvest: