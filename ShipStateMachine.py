#!/usr/bin/env python3
# Python 3.6

import hlt
from hlt import constants
from hlt.positionals import Direction
import random
import logging
import helperfunctions
import gc

from enum import Enum     # for enum34, or the stdlib version
# from aenum import Enum  # for the aenum version
ShipState = Enum('ShipState', 'north east south west returnHome harvest')

def StateMachine(game, CQueue, state,ship):
  if state == ShipState.north:
    pass
  elif state == ShipState.east:
    pass
  elif state == ShipState.south:
    pass
  elif state == ShipState.west:
    pass
  elif state == ShipState.returnHome:
    gc.ShipInfos[ship.id].ReturnHome = True
    MoveQueue = helperfunctions.ShortestPath( game.game_map, ship.position, game.me.shipyard.position )
    if not MoveQueue:
      logging.info("Not returning home anymore")
      gc.ShipInfos[ship.id].ReturnHome = False
    else:
      CQueue.append( ship.move( MoveQueue[0] ))
  elif state == ShipState.harvest:
    pass