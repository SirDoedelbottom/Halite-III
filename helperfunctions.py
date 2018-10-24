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
    self.MiningCounter = -1
    self.MiningRounds = 0
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
      ship.MiningCounter = shipInfos[ship.id].MiningCounter
      ship.MiningRounds = shipInfos[ship.id].MiningRounds
  #return shipInfos

def SaveShipInfos(shipInfos, ships):
  shipInfos = {}
  for ship in ships:
    SI = ShipInfo()

    SI.ReturnHome = ship.ReturnHome
    SI.Expand = ship.Expand
    SI.Home = ship.Home
    SI.Destination = ship.Destination
    SI.MiningCounter = ship.MiningCounter
    SI.MiningRounds = ship.MiningRounds
    shipInfos[ship.id] = SI
  return shipInfos

def FindClosestValidSpot( game_map, ShipPos, max_dist, ShipBellMap, InvalidSpots = [], threshold = 75 ):
  """ Returns the position of the closest valid spot (not blocked, enough halite avaliable) within the given range """
  BestSpot = False               # default: stay still
  maxDist = 5
  RepellantFactor = 1
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
      Corr = ((maxDist-dist)/maxDist)*RepellantFactor
      Halite = (ShipBellMap[Spot.x][Spot.y] + Corr) * game_map[Spot].halite_amount
      if Halite >= max(threshold, max_amount) and Spot not in InvalidSpots:
        BestSpot = Spot
        max_amount = Halite
        Found = True
    if Found == True:
      return BestSpot
  if not BestSpot:
    logging.info("No Spot found: calling myself again")
    return FindClosestValidSpot(game_map, ShipPos, max_dist+3, ShipBellMap, InvalidSpots, threshold*0.75)
  return BestSpot
  
def getAllEnemyFields( game ):
  EnemyFields = []
  for Enemy in game.players:
    if Enemy == game.me.id:
      continue
    #EnemyFields.extend(game.players[Enemy].get_ships())
    for ship in game.players[Enemy].get_ships():
       #EnemyFields.extend([ship.position]+ship.position.get_surrounding_cardinals())
       EnemyFields.append(ship.position)
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

def SortShipsByDistance(game_map, ships, position):
  def distance(ship):
    #bei schiffen gleicher distanz werden zu erst die schiffe weiter links genommen
    value = 0
    if ship.halite_amount * 10 < game_map[ship.position].halite_amount:
      value= -1
    else:
      value = game_map.calculate_distance(ship.position,ship.Home)+(ship.position.x/100)
    logging.info("ship id: " + str(ship.id) + " hat value: " + str(value))
    return value
  ships.sort(key=distance)
  logging.info(ships)
  return ships



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

def GetShipBellMap( ships, game_map, maxDist=5, RepellantFactor=1 ):
  BellMap = np.zeros((game_map.width, game_map.height))
  height = game_map.height
  width = game_map.width
  for ship in ships:
    ShipPos = ship.position
    for dist in range(maxDist+1):
      for i in range(dist):
        BellMap[(ShipPos.x+i) % width][ShipPos.y-dist+i % height] += (maxDist-dist)/maxDist*RepellantFactor
        BellMap[(ShipPos.x+dist-i) % width][(ShipPos.y+i) % height] += (maxDist-dist)/maxDist*RepellantFactor
        BellMap[(ShipPos.x-i) % width][(ShipPos.y+dist-i) % height] += (maxDist-dist)/maxDist*RepellantFactor
        BellMap[(ShipPos.x-dist+i) % width][(ShipPos.y-i) % height] += (maxDist-dist)/maxDist*RepellantFactor
  return BellMap



def DijkstraField( game_map, shipPos, distance, invalidSpots):
  field = {}
  candidates = GetPointsInDistance(game_map, distance,shipPos,invalidSpots)
  while len(candidates) > 0:
    #currentPosition = min(candidates, key=getTuple)
    lowestValue = np.inf
    currentPosition = None
    for c in candidates:
      if candidates[c][0] <= lowestValue:
        lowestValue = candidates[c][0]
        currentPosition = c
    # logging.info(currentPosition)
    # logging.info(candidates)
    currentTuple = candidates.pop(currentPosition)
    
    field[currentPosition] = (currentTuple[0], currentTuple[1])

    cardinals = currentPosition.get_surrounding_cardinals()
    for cardinal in cardinals:
      cardinal = game_map.normalize(cardinal)
      if cardinal in candidates:
        if(currentTuple[0]+1 < candidates[cardinal][0]):
          candidates[cardinal] = (currentTuple[0] + 1,currentPosition)
  return field


def closestReachablePositionToPosition(game_map, field, position):
  closestPosition = None
  closestDistance = np.inf
  for f in field:
    currentDistance = game_map.calculate_distance(f,position)
    if currentDistance < closestDistance and field[f][1] is not None:
      closestDistance = currentDistance
      closestPosition = f
  return closestPosition


def GetDirectionToDestination(game_map,ship,destination,invalidSpots):
  distance = game_map.calculate_distance(ship.position, destination)
  field = DijkstraField(game_map,ship.position,distance+1,invalidSpots)
  currentPosition = destination
  logging.info(currentPosition)
  logging.info(field)
  if currentPosition is None:
    logging.info("No where to go. gg")
    return Direction.Still

  if currentPosition not in field: #already blocked
    currentPosition = closestReachablePositionToPosition(game_map,field,destination)
  logging.info(currentPosition)
  if field[currentPosition][1] is None: #unreachable
    currentPosition = closestReachablePositionToPosition(game_map,field,destination)

  logging.info(currentPosition)
  logging.info(ship.position)
  logging.info(destination)
  if currentPosition is None:
    logging.info("No where to go. gg")
    return Direction.Still
  if currentPosition==ship.position:
    if ship.position in invalidSpots:
      ca = ship.position.get_surrounding_cardinals()
      for c in ca:
        c = game_map.normalize(c)
        if c not in invalidSpots:
          return game_map.get_unsafe_moves(ship.position, c)[0]
        
    else:
      return Direction.Still
  while field[currentPosition][1]!=ship.position:
    currentPosition = field[currentPosition][1]
  return game_map.get_unsafe_moves(ship.position, currentPosition)[0]


def FindEfficientSpot(game_map,ship,distance,invalidSpots):
  field = DijkstraField(game_map,ship.position,distance,invalidSpots)
  for f in field:
    path = GetDijkstraPath(field,f)
    #kosten zum punkt
    kosten = 0
    for position in path:
      # if kosten == -1: #destination kosten muss man nicht bezahlen
      #   kosten = 0
      #   continue
      kosten += game_map[position].halite_amount
    DurschnittsAbbauRaten=[]

    homeDistance = game_map.calculate_distance(f, ship.Home)
    for i in range(1,10):
      
      DurschnittsAbbauRate = (game_map[f].halite_amount *( 1-0.75**(i-field[f][0]))-kosten)/(i+homeDistance)
      DurschnittsAbbauRaten.append(DurschnittsAbbauRate)
    index = np.argmax(DurschnittsAbbauRaten)
    platz_im_schiff_verbleibend = 1000-ship.halite_amount
    halite_am_spot = game_map[f].halite_amount
    if halite_am_spot > platz_im_schiff_verbleibend:
      turns_bis_voll = int(np.log(1-(platz_im_schiff_verbleibend/halite_am_spot)) / np.log(0.75))
      if turns_bis_voll < index:
        index = turns_bis_voll
    field[f] =(field[f][0],field[f][1],index-field[f][0],DurschnittsAbbauRaten[index],path)
  highestValue = -np.inf
  destination = None
  for f in field:
    if field[f][3] >= highestValue and f not in invalidSpots:
      highestValue = field[f][3]
      destination = f
  logging.info(destination)
  if destination is None:
    logging.info(field)
    logging.info(invalidSpots)
  if destination is None:
    return Direction.Still
  #destination = max(field, key=field[3].get)
  ship.MiningRounds = field[destination][2]
  if len(field[destination][4]) == 0:
    direction = Direction.Still
  elif len(field[destination][4]) == 1:
    direction = game_map.get_unsafe_moves(ship.position, destination)[0]
  else:
    direction = game_map.get_unsafe_moves(ship.position, field[destination][4][-2])[0]
    #logging.info(field[destination][4][-2])
  #logging.info(direction)
  return direction

  
def GetDijkstraPath(field, destination):
  path = []
  spot = field[destination]
  while spot is not None:
    if spot[1] in field:
      path.append(spot[1])
      spot = field[spot[1]]
    else:
      spot = None
  return path


def GetPointsInDistance(game_map, distance, position,invalidSpots):
  distance
  positions ={}
  #if position not in invalidSpots:
  positions[position] = (0,None)
  for dist in range(1,distance):
    for i in range(dist):
      poss =[]
      poss.append(game_map.normalize(Position(position.x+i,position.y-dist+i)))
      poss.append(game_map.normalize(Position(position.x+dist-i,position.y+i)))
      poss.append(game_map.normalize(Position(position.x-i,position.y+dist-i)))
      poss.append(game_map.normalize(Position(position.x-dist+i,position.y-i)))
      for p in poss:
        if p not in invalidSpots and p not in positions:
          positions[p] = (np.inf,None)
  return positions



    
