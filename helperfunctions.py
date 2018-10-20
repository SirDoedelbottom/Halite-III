#!/usr/bin/env python3
# Python 3.6
import hlt
from hlt import constants
from hlt.positionals import Direction
import random
import logging

#import MyBot

def ShortestPath( game_map, ShipPos, DestPos ):
  MoveQueue=[]
  diffX = DestPos.x - ShipPos.x
  diffY = DestPos.y - ShipPos.y

  if abs(diffX - game_map.width) < abs(diffX):
    diffX -= game_map.width
  if abs(diffY - game_map.height) < abs(diffY):
    diffY -= game_map.height
    
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
    self.Priority = 0
    self.Task

def RefreshDict( Dict, hltShips ):
  for ship in hltShips:
    if ship.id not in Dict:
      #append ShipInfo to dict:
      Dict[ship.id]=ShipInfo()

def SetWishPos(shipID, pos, colMap):
  i = 0
  while i > -1
    if colMap[pos.x][pos.y][i] == 0
      colMap[pos.x][pos.y][i] = shipID
      i = -1
    else
      i++

def ResolveCollisionMap (colMap,conflicts,ShipInfos)
  newConflict = false
  for x in range(colMap.shape(0)):
    for y in range(colMap.shape(1)):
        if colMap[x][y][1] !=0
          XYConflict = colMap[x][y]
          np.trim_zeros(XYConflict, 'b')
          HPSID = 0
          highestPrio = -1
          for i in range(XYConflict)
            currentPrio = ShipInfos[XYConflict[i]].Priority
            if currentPrio > highestPrio
              highestPrio = currentPrio
              HPSID = XYConflict[i]
          colMap[x][y][0] = HPSID
          for i in range(0,XYConflict)
            if i > 0
              colMap[x][y][i] = 0
            if XYConflict[i] != HPSID
              conflicts[colMap[x][y][i]].append((x,y))
              newConflict = true
  if newConflict
    return false
  else
    return true
