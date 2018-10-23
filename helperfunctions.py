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
    self.Expand = False
    self.Home = None
    self.Destination = None
  def __repr__(self):
    return "{}(Expand={}, Destination={})".format(self.__class__.__name__,
                                                       self.Expand,
                                                       self.Destination)


def LoadShipInfos(shipInfos, ships):
  for ship in ships:
    if ship.id in shipInfos:
      ship.ReturnHome = shipInfos[ship.id].ReturnHome
      ship.Expand = shipInfos[ship.id].Expand
      ship.Home = shipInfos[ship.id].Home
      ship.Destination = shipInfos[ship.id].Destination
  #return shipInfos

def SaveShipInfos(shipInfos, ships):
  shipInfos = {}
  for ship in ships:
    SI = ShipInfo()

    SI.ReturnHome = ship.ReturnHome
    SI.Expand = ship.Expand
    SI.Home = ship.Home
    SI.Destination = ship.Destination
    shipInfos[ship.id] = SI
  return shipInfos

def FindClosestValidSpot( game_map, ShipPos, max_dist, InvalidSpots = [], threshold = 75 ):
  """ Returns the position of the closest valid spot (not blocked, enough halite avaliable) within the given range """
  BestSpot = False               # default: stay still
  for dist in range(max_dist):     # iterate over distances
    # get Spots with this range
    Spots = []
    for i in range(dist+1):
      # CAUTION: dir_offset might not work with i>1!!
      Spots.append( game_map.normalize(Position(ShipPos.x+i,ShipPos.y-dist+i)) )
      Spots.append( game_map.normalize(Position(ShipPos.x-i,ShipPos.y+dist-i)) )
      Spots.append( game_map.normalize(Position(ShipPos.x+dist-i,ShipPos.y+i)) )
      Spots.append( game_map.normalize(Position(ShipPos.x-dist+i,ShipPos.y-i)) )
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
    return FindClosestValidSpot(game_map, ShipPos, max_dist+3, InvalidSpots, threshold*0.67)
  return BestSpot
  
def getAllEnemyFields( game ):
  EnemyFields = []
  for Enemy in game.players:
    if Enemy == game.me.id:
      continue
    for ship in game.players[Enemy].get_ships():
      EnemyFields.extend([ship.position]+ship.position.get_surrounding_cardinals())
  EnemyFields = list(set(EnemyFields))
  return EnemyFields

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
      tempCandidates.append(game_map.normalize(current[0].directional_offset(tc)))
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
        EastSpot = game_map.normalize(ShipPos.directional_offset(Direction.East))
        WestSpot = game_map.normalize(ShipPos.directional_offset(Direction.West))
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
        SouthSpot = game_map.normalize(ShipPos.directional_offset(Direction.South))
        NorthSpot = game_map.normalize(ShipPos.directional_offset(Direction.North))
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
          if game_map.normalize(ShipPos.directional_offset(BackDir)) not in InvalidSpots:
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

def ResolveCollisionMap (colMap,conflicts,ships):
  newConflict = False
  for x in range(colMap.shape[0]):
    for y in range(colMap.shape[1]):
        if colMap[x][y][1] != -1:
          XYConflict = colMap[x][y]
          XYConflict = np.array([int(i) for i in XYConflict])
          try:
            FirstNegIdx = np.where(XYConflict == -1)[0][0]
          except IndexError:
            FirstNegIdx = XYConflict.shape[0]
          XYConflict = XYConflict[0:FirstNegIdx]
          HPSID = 0
          highestPrio = -1
          for i in XYConflict:
            ship = None
            #get the ship with id i
            for ship in ships:
              if ship.id == i:
                break
              else:
                ship = None
            currentPrio = ship.Priority
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

def closestShipToPosition(game_map, ships, position,count = 1, ignoreShips = []):
  closestShips = []
  for i in range(count):
    closestShip = None
    closestDistance = np.inf
    for ship in ships:
      if ship in ignoreShips+closestShips:
        continue
      currentDistance = game_map.calculate_distance(ship.position,position)
      if currentDistance < closestDistance:
        closestDistance= currentDistance
        closestShip = ship
    closestShips.append(closestShip)
  return closestShips

def GetExpandingShip(ships):
  for ship in ships:
    if ship.Expand == True:
      return ship
  return None

def GetPotentialExpansions(game_map, emap,position):
  """Returns a List of Potential Expansions in Range of 10% of the max Value sorted by distance to position"""
  maxValue = np.amax(emap)
  PoExPositions = []
  for x in range(emap.shape[0]):
    for y in range(emap.shape[1]):
      if emap[x,y] / maxValue > 0.9 and not game_map[Position(x,y)].has_structure:        #10% in range of maxValue
        PoExPositions.append(Position(x,y))
  def distance(pos):
    return game_map.calculate_distance(pos,position)
  PoExPositions.sort(key=distance)
  return PoExPositions