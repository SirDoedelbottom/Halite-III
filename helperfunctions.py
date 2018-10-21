#!/usr/bin/env python3
# Python 3.6
import hlt
from hlt import constants
from hlt.positionals import Direction
from hlt.positionals import Position
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


def FindClosestValidSpot( game_map, ShipPos, max_dist, InvalidSpots = [], threshold = 75 ):
  """ Returns the position of the closest valid spot (not blocked, enough halite avaliable) within the given range """
  BestSpot = False               # default: stay still
  for dist in range(max_dist):     # iterate over distances
    # get Spots with this range
    Spots = []
    for i in range(dist+1):
      # CAUTION: dir_offset might not work with i>1!!
      Spots.append( game_map.normalize(Position(ShipPos.x+i,ShipPos.y+dist-i)) )
      Spots.append( game_map.normalize(Position(ShipPos.x-i,ShipPos.y-dist+i)) )
    # check Halite threshold on Spots
    max_amount = -1
    Found = False
    for Spot in Spots:
      if game_map[game_map.normalize(Spot)].halite_amount >= max(threshold,max_amount) and Spot not in InvalidSpots:
        BestSpot = Spot
        max_amount = game_map[game_map.normalize(Spot)].halite_amount
        Found = True
    if Found == True:
      return BestSpot
  if not BestSpot:
    logging.info("No Valid Spot found for Ship with ID: " + str(game_map[ShipPos].ship.id))
    return FindClosestValidSpot(game_map, ShipPos, max_dist+3, InvalidSpots, threshold*0.67)
  return BestSpot
  

def FindCheapestShortestRoute( game_map, ShipPos, DestPos, InvalidSpots = [] ):
  """ Find the Cheapest Route, but only out of the shortest Routes. (Don't even consider non-shortest Routes) """
  VisitedSpots = []   # (Position, BestPrev, BestCost)
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
              candidates.append((tC,current[0],cost))
            break 
        if not nominated:
          candidates.append((tC,current[0],cost))
      else:
        pass
  curNode = VisitedSpots[-1]
  path =[]
  while curNode[0]!=ShipPos:
    path.insert(0,curNode[0])
    for VS in VisitedSpots:
      if VS[0] == curNode[1]:
        curNode = VS
  #path.insert(0,curNode[0])
  if len(path) == 0:
    if ShipPos in InvalidSpots:
      if ShipPos.x == DestPos.x:
        EastSpot = ShipPos.directional_offset(Direction.East)
        WestSpot = ShipPos.directional_offset(Direction.West)
        if WestSpot not in InvalidSpots and EastSpot not in InvalidSpots:
          if game_map[ EastSpot].halite_amount > game_map[WestSpot].halite_amount:
            return Direction.East
          else:
            return Direction.West
        elif WestSpot not in InvalidSpots:
          return Direction.West
        elif EastSpot not in InvalidSpots:
          return Direction.East
        else: # back it up
          BackDir = Direction.Still
          if ShipPos.y > DestPos.y:
            BackDir = Direction.South
          else:
            BackDir = Direction.North
          if ShipPos.directional_offset(BackDir) not in InvalidSpots:
            return BackDir
      elif ShipPos.y == DestPos.y:
        SouthSpot = ShipPos.directional_offset(Direction.South)
        NorthSpot = ShipPos.directional_offset(Direction.North)
        if SouthSpot not in InvalidSpots and NorthSpot not in InvalidSpots:
          if game_map[ SouthSpot].halite_amount > game_map[NorthSpot].halite_amount:
            return Direction.South
          else:
            return Direction.North
        elif NorthSpot not in InvalidSpots:
          return Direction.North
        elif SouthSpot not in InvalidSpots:
          return Direction.South
        else: # back it up
          BackDir = Direction.Still
          if ShipPos.x > DestPos.x:
            BackDir = Direction.East
          else:
            BackDir = Direction.West
          if ShipPos.directional_offset(BackDir) not in InvalidSpots:
            return BackDir
    else:
      return Direction.Still
    return Direction.Still
  return game_map.get_unsafe_moves(ShipPos, path[0])[0]

def SetWishPos(shipID, pos, colMap):
  
  i = 0
  while i > -1:
    if colMap[pos.x][pos.y][i] == -1:
      colMap[pos.x][pos.y][i] = shipID
      i = -1
    else:
      i+=1

def ResolveCollisionMap (colMap,conflicts,ShipInfos):
  newConflict = False
  for x in range(colMap.shape[0]):
    for y in range(colMap.shape[1]):
        if colMap[x][y][1] != -1:
          XYConflict = colMap[x][y]
          #XYConflict = np.trim_zeros(XYConflict, 'b')
          XYConflict = np.array([int(i) for i in XYConflict])
          logging.info(XYConflict)
          try:
            FirstNegIdx = np.where(XYConflict == -1)[0][0]
          except IndexError:
            FirstNegIdx = XYConflict.shape[0]
          XYConflict = XYConflict[0:FirstNegIdx]
          HPSID = 0
          highestPrio = -1
          for i in XYConflict:
            currentPrio = ShipInfos[i].Priority
            if currentPrio > highestPrio:
              highestPrio = currentPrio
              HPSID = i
          colMap[x][y][0] = HPSID
          h = 0
          for i in XYConflict:
            if h != 0:
              colMap[x][y][h] = -1
            h+=1
            if i != HPSID:
              if not i in conflicts:
                conflicts[i] = []
              conflicts[i].append(Position(x,y))
              newConflict = True
  if newConflict:
    return True
  else:
    return False
