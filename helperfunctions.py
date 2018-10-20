#!/usr/bin/env python3
# Python 3.6
import hlt
from hlt import constants
from hlt.positionals import Direction
import random
import logging
import numpy as np
 
#import MyBot

def ShortestPath( game_map, ShipPos, DestPos ):
  MoveQueue=[]
  diffX = DestPos.x - ShipPos.x
  diffY = DestPos.y - ShipPos.y

  if abs(diffX - game_map.width) < abs(diffX):
    diffX -= game_map.width
  if abs(diffY - game_map.height) < abs(diffY):
    diffY -= game_map.height
    
  if diffX < 0:
    MoveQueue.extend( [Direction.West]*abs(diffX) )  
  else:
    MoveQueue.extend( [Direction.East]*abs(diffX) )  
  if diffY < 0:
    MoveQueue.extend( [Direction.North]*abs(diffY) )
  else:
    MoveQueue.extend( [Direction.South]*abs(diffY) )
  return MoveQueue

class ShipInfo:
  def __init__(self):
    self.ReturnHome = False
    self.Priority = 0
    self.Direction = Direction.Still

def RefreshDict( Dict, hltShips ):
  for ship in hltShips:
    if ship.id not in Dict:
      #append ShipInfo to dict:
      Dict[ship.id]=ShipInfo()


def FindClosestValidSpot( game_map, ShipPos, max_dist, InvalidSpots = [], threshold = 100 ):
  """ Returns the position of the closest valid spot (not blocked, enough halite avaliable) within the given range """
  BestSpot = ShipPos                  # default: stay still
  for dist in range(max_dist):     # iterate over distances
    # get Spots with this range
    Spots = []
    for i in range(dist):
      Spots.append( ShipPos.directional_offset( (i,dist-i) ) )
      Spots.append( ShipPos.directional_offset( (-i,-dist+i) ) )
    # check Halite threshold on Spots
    max_amount = -1
    for Spot in Spots:
      if game_map[game_map.normalize(Spot)].halite_amount >= max(threshold,max_amount) and Spot not in InvalidSpots:
        BestSpot = Spot
        max_amount = game_map[game_map.normalize(Spot)].halite_amount
    if BestSpot != ShipPos:
      break
  return BestSpot

def FindCheapestShortestRoute( game_map, ShipPos, DestPos, InvalidSpots = [] ):
  """ Find the Cheapest Route, but only out of the shortest Routes. (Don't even consider non-shortest Routes) """
  VisitedSpots = [(ShipPos, ShipPos, 0)]   # (Position, BestPrev, BestCost)
  candidates = [(ShipPos, ShipPos, 0)]
  if ShipPos == DestPos:
    return Direction.Still
  # evaluate all Spots with dist and possibly add to "to_process_list"
  while len (candidates) !=0:
    current = candidates.pop(0)
    VisitedSpots.append(current)
    tempCandidatesDir = game_map.get_unsafe_moves(current[0], DestPos)
    tempCandidates = []
    for tc in tempCandidatesDir:
      tempCandidates.append(current[0].directional_offset(tc))
    for tC in tempCandidates:
      cost = game_map[tC].halite_amount/10 + current[2]
      if tC not in InvalidSpots:
        nominated = False
        for no in candidates:
          if no[0] == tC:
            nominated = True
            if no[2] > cost:
              candidates.remove(no)
              candidates.append((tC,current,cost))
            break 
        if not nominated:
          candidates.append((tC,current,cost))
  curNode = VisitedSpots[-1]
  path =[]
  while curNode[0]!=ShipPos:
    path.insert(0,curNode[0])
    for VS in VisitedSpots:
      if VS[0] == curNode[1]:
        curNode = VS
  return game_map.get_unsafe_moves(path[0], path[1])

def SetWishPos(shipID, pos, colMap):
  i = 0
  while i > -1:
    if colMap[pos.x][pos.y][i] == 0:
      colMap[pos.x][pos.y][i] = shipID
      i = -1
    else:
      i+=1

def ResolveCollisionMap (colMap,conflicts,ShipInfos):
  newConflict = False
  for x in range(colMap.shape[0]):
    for y in range(colMap.shape[1]):
        if colMap[x][y][1] !=0:
          XYConflict = colMap[x][y]
          np.trim_zeros(XYConflict, 'b')
          HPSID = 0
          highestPrio = -1
          for i in range(XYConflict):
            currentPrio = ShipInfos[XYConflict[i]].Priority
            if currentPrio > highestPrio:
              highestPrio = currentPrio
              HPSID = XYConflict[i]
          colMap[x][y][0] = HPSID
          for i in range(0,XYConflict):
            if i > 0:
              colMap[x][y][i] = 0
            if XYConflict[i] != HPSID:
              conflicts[colMap[x][y][i]].append((x,y))
              newConflict = True
  if newConflict:
    return True
  else:
    return False
