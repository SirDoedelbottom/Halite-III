#!/usr/bin/env python3
# Python 3.6

import hlt
from hlt import constants
from hlt.positionals import Direction
import random
import logging

def ShortestPath( ShipPos, DestPos ):
  MoveQueue=[]
  diffX = DestPos.x - ShipPos.x
  diffY = DestPos.y - ShipPos.y

  for i in range(abs(diffX)):
    if diffX < 0:
      MoveQueue.append(Direction.West)  
    else:
      MoveQueue.append(Direction.East) 
  for i in range(abs(diffY)):
    if diffY < 0:
      MoveQueue.append(Direction.North)
    else:
      MoveQueue.append(Direction.South)
  return MoveQueue

class ShipInfo:
  def __init__(self):
    self.ReturnHome = False

def RefreshDict( Dict, hltShips ):
  for ship in hltShips:
    if ship.id not in Dict:
      #append ShipInfo to dict:
      Dict[ship.id]=ShipInfo()
