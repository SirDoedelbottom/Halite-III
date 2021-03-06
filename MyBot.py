#!/usr/bin/env python3
# Python 3.6

import hlt
from hlt import constants
from hlt.positionals import Direction
from hlt.positionals import Position
import logging
import helperfunctions as hf
import numpy as np
from enum import Enum     # for enum34, or the stdlib version

game = hlt.Game()

""" <<<Game Begin>>> """



# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("MyPythonBot")
ShipState = Enum('ShipState', 'north east south west returnHome harvest')
reservedHalite = 0
DropOffPending = False
NextExpansion = None
ShipInfos = {}
lastExpansion = 0
# ShipBellMap = hf.GetShipBellMap( game.me.get_ships(), game.game_map )


logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

def EvaluatePoint(position):
  maxDist = 6
  positionValue = game_map[position].halite_amount
  for dist in range(1,maxDist):
    for i in range(dist):
      positionValue+= int(game_map[game_map.normalize(Position(position.x+i,position.y-dist+i))].halite_amount * (1 - i/(dist+1)))
      positionValue+= int(game_map[game_map.normalize(Position(position.x+dist-i,position.y+i))].halite_amount * (1 - i/(dist+1)))
      positionValue+= int(game_map[game_map.normalize(Position(position.x-i,position.y+dist-i))].halite_amount * (1 - i/(dist+1)))
      positionValue+= int(game_map[game_map.normalize(Position(position.x-dist+i,position.y-i))].halite_amount * (1 - i/(dist+1)))
  return positionValue

def EvaluateMap(ships):
  evaluatedMap = np.zeros([game_map.width,game_map.height])
  for s in ships:
    x = s.position.x
    y = s.position.y

  # for x in range(game_map.width):
  #   for y in range(game_map.height):
    evaluatedMap[x,y] = EvaluatePoint(Position(x,y))
  return evaluatedMap

  
def whatDo(ship, blocked = []):
  departure = me.shipyard.position == ship.position
  ship.Priority = -1
  wishDirection = Direction.Still
  wishPosition = ship.position
  for do in me.get_dropoffs():
    if do.position == ship.position:
      departure = True

  #logging.info("Ship ID = " + str(ship.id) + ", Mining Counter = " + str(ship.MiningCounter))

  if departure:
    ship.Priority = 3
    ship.ReturnHome = False
  #####Checken ob das klar geht mit neuer collision wenn schiffe leer sind
  if ship.halite_amount < np.ceil(game_map[ship.position].halite_amount/10):  # Out of Fuel
    #ship.Priority = 4
    #hf.SetWishPos(ship.id,game_map.normalize(ship.position), collisionMap)
    wishPosition = game_map.normalize(ship.position)
    wishDirection = Direction.Still
  elif RushHome:
    # find closest Spot to home:
    home = ship.Home
    homeCardinals = []
    for ca in home.get_surrounding_cardinals():
      homeCardinals.append(game_map.normalize(ca))
    if ship.position in homeCardinals:
      wishDirection = game_map.get_unsafe_moves(ship.position, home)[0]
    else: # not in surrounding cardinals => navigate to BestRetSpot
      ship.Priority = 2
      #wishDirection = hf.FindCheapestShortestRoute( game_map, ship.position, home, blocked )
      wishDirection = hf.GetAStarPath(game_map, ship.position, home,blocked+EnemyFields)
      #hf.SetWishPos(ship.id,game_map.normalize(ship.position.directional_offset(wishDirection)), collisionMap)
      wishPosition = game_map.normalize(ship.position.directional_offset(wishDirection))
  elif ship.Expand == True: #Expanding
    ship.Priority = 3
    if ship.position == NextExpansion and not game_map[NextExpansion].has_structure and me.halite_amount + ship.halite_amount + game_map[ship.position].halite_amount >= 4000:
      command_queue.append(ship.make_dropoff())
      wishDirection = None
      global DropOffPending 
      DropOffPending = True
    else:
      #wishDirection = hf.FindCheapestShortestRoute( game_map, ship.position, NextExpansion,blocked+EnemyFields )
      wishDirection = hf.GetAStarPath(game_map, ship.position, NextExpansion,blocked+EnemyFields)
      #hf.SetWishPos(ship.id,game_map.normalize(ship.position.directional_offset(wishDirection)), collisionMap)
      wishPosition = game_map.normalize(ship.position.directional_offset(wishDirection))
  elif ship.Destination is not None: ##muss noch allgemeiner gemacht werden 4000 gerade nur damit die icht zu früh losfahren
    if ship.position == ship.Destination:
      ship.Destination = None
      wishDirection=hf.AStarFindEfficientSpot(game_map,ship,7,blocked+EnemyFields)
      wishPosition = game_map.normalize(ship.position.directional_offset(wishDirection))
    else:
      ship.Priority = 1
      #wishDirection = hf.FindCheapestShortestRoute( game_map, ship.position,ship.Destination,blocked+EnemyFields )
      wishDirection = hf.GetAStarPath(game_map, ship.position, ship.Destination,blocked+EnemyFields)

      #hf.SetWishPos(ship.id,game_map.normalize(ship.position.directional_offset(wishDirection)), collisionMap)
      wishPosition = game_map.normalize(ship.position.directional_offset(wishDirection))

  elif ship.halite_amount >= 950 or ship.ReturnHome:  # return home!
    #ship.Priority = 1
    #wishDirection = hf.FindCheapestShortestRoute( game_map, ship.position,ship.Home,blocked+EnemyFields )
    if ship.Home is None:
      ship.Home = me.shipyard.position
    wishDirection = hf.GetAStarPath(game_map, ship.position, ship.Home,blocked+EnemyFields)
    #hf.SetWishPos(ship.id,game_map.normalize(ship.position.directional_offset(wishDirection)), collisionMap)
    wishPosition = game_map.normalize(ship.position.directional_offset(wishDirection))
    ship.ReturnHome = True

  elif False and ship.MiningCounter > -1 and ship.position not in blocked:
    if ship.MiningCounter >= ship.MiningRounds:
      ship.MiningCounter = -1
    elif len(blocked) == 0:
      ship.MiningCounter += 1
    wishDirection = Direction.Still
    #hf.SetWishPos(ship.id,ship.position, collisionMap)
    wishPosition = ship.position
    ship.Priority = 3
  else:
    #wishDirection=hf.FindEfficientSpot(game_map,ship,7,blocked+EnemyFields)
    wishDirection=hf.AStarFindEfficientSpot(game_map,ship,7,blocked+EnemyFields)
    #logging.info(wishDirection)
    wishPosition = game_map.normalize(ship.position.directional_offset(wishDirection))
  # else: # find closest valid spot
  #   logging.info("Inside Else")
  #   wishSpot = hf.FindClosestValidSpot(game_map, ship.position, 32, ShipBellMap, blocked)
  #   ship.Destination = wishSpot
  #   if wishSpot == ship.position and len(blocked) == 0:
  #     ship.MiningCounter = 0
  #   wishDirection = hf.FindCheapestShortestRoute(game_map,ship.position,wishSpot,blocked+EnemyFields)
  #   if ship.Priority == -1:
  #     if wishDirection == Direction.Still:
  #       ship.Priority = 1 
  #     else:
  #       ship.Priority = 0
  #   #hf.SetWishPos(ship.id,game_map.normalize(ship.position.directional_offset(wishDirection)), collisionMap)
  #   wishPosition = game_map.normalize(ship.position.directional_offset(wishDirection))
  #if(wishDirection != None):
  ship.Direction = wishDirection
  return wishPosition

""" <<<Game Loop>>> """
while True:
  game.update_frame()


  me = game.me
  game_map = game.game_map
  command_queue = []
  collisionMap = np.ones((game.game_map.width,game.game_map.height,5))
  collisionMap = -collisionMap
  RushHome = False
  ShipDistList = []
  EnemyFields = hf.getAllEnemyFields( game )
  hf.LoadShipInfos(ShipInfos, me.get_ships())
  # ShipBellMap = hf.GetShipBellMap( me.get_ships(), game_map )
  collisionList = []

  for ship in me.get_ships():
    MinDist = np.inf
    BestRetSpot = None
    Dropoffs = me.get_dropoffs()
    RetSpots = [me.shipyard.position]
    for DropOff in Dropoffs:
      RetSpots.append(DropOff.position)
    for RetSpot in RetSpots:
      CurDist = game_map.calculate_distance(RetSpot, ship.position)
      if CurDist < MinDist:
        MinDist = CurDist
        BestRetSpot = RetSpot
    ship.Home = BestRetSpot
  for ship in me.get_ships():
    DistToHome = game_map.calculate_distance(me.shipyard.position, ship.position)
    for DropOff in me.get_dropoffs():
      DistToDropoff = game_map.calculate_distance(DropOff.position, ship.position)
      if DistToDropoff < DistToHome:
        DistToHome = DistToDropoff
    ShipDistList.append( (ship.id, DistToHome) )
  ShipDistList.sort(key=lambda tup: tup[1])
  MaxDistShips = 0
  if len(ShipDistList) != 0:
    MaxDist = ShipDistList[-1][1]
  else:
    MaxDist = 0
  for ShipDist in ShipDistList:
    if ShipDist[1] ==  ShipDistList[-1][1]:
      MaxDistShips += 1
  if (constants.MAX_TURNS - game.turn_number) - (MaxDist+MaxDistShips) <= 0: # safty Distance 
    RushHome = True


  if lastExpansion + 50 < game.turn_number and constants.MAX_TURNS - game.turn_number > 50:
    averageHomeDistance = 0
    for ship in me.get_ships():
      averageHomeDistance += game_map.calculate_distance(ship.position, ship.Home)
    if len(me.get_ships()) > 0:
      averageHomeDistance= averageHomeDistance/ len(me.get_ships())
    ExpansionNeeded = False
    emap = []
    if averageHomeDistance > 6 :
      emap = EvaluateMap(me.get_ships())
      gamePercentage = .75+(game.turn_number / constants.MAX_TURNS)/2
      if np.amax(emap) * gamePercentage > 5000: #testing
        ExpansionNeeded = True
  
    if ExpansionNeeded:
      ExpansionShip = hf.GetExpandingShip(me.get_ships())
      #logging.info("Expansion Ship is : " + str(ExpansionShip))
      #logging.info("ShipInfos : " + str(ShipInfos))
      if ExpansionShip is None:
        for ship in me.get_ships():
          ship.Destination = None
        reservedHalite = 4000
        #emap = EvaluateMap(me.get_ships())
        NextExpansion = hf.GetPotentialExpansions(game_map,emap,me.shipyard.position)[0]
        ExpansionShip=hf.closestShipToPosition(game_map,me.get_ships(),NextExpansion)[0]
        ExpansionShip.Expand = True
      else:
        if game_map[NextExpansion].has_structure:
          ExpansionShip.Expand = False
    
  sortedShips = hf.SortShipsByDistance(game_map,me.get_ships(),me.shipyard.position)
  
  for ship in sortedShips:
    collisionList.append(whatDo(ship,collisionList))
  # conflicts = {}
  # counter = 10
  # while hf.ResolveCollisionMap(collisionMap,conflicts, me.get_ships()):
  #   counter -= 1
  #   if counter == 0:
  #     logging.info("can't resolve conflicts: " + str(conflicts))
  #     break
  #   for key in conflicts:
  #     whatDo(me.get_ship(key),conflicts[key])
  for ship in me.get_ships():
    
    if ship.Direction != None:
      command_queue.append(ship.move(ship.Direction))
    else:
        logging.info("HOW THE FUCK DID WE GET HERE")

  maximum = 0
  for p in game.players:
    if p != me.id:
      shipCount = len(game.players[p].get_ships())
      if shipCount > maximum:
        maximum = shipCount
  if maximum < 30:
    maximum = 30
  # If the game is in the first 200 turns and you have enough halite, spawn a ship.
  # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
  if len(me.get_ships())  <= maximum * 1.1 and game.turn_number <= constants.MAX_TURNS*4/7 and me.halite_amount - reservedHalite >= constants.SHIP_COST and me.shipyard.position not in collisionList: #collisionMap[me.shipyard.position.x][me.shipyard.position.y][0]==-1:
    command_queue.append(me.shipyard.spawn())
  if DropOffPending == True:
    lastExpansion = game.turn_number
    ExpansionGroup = hf.closestShipToPosition(game_map,me.get_ships(),NextExpansion,4,[ExpansionShip])
    i = 0
    for ship in ExpansionGroup:
      if ship is not None:
        ship.Destination = NextExpansion.get_surrounding_cardinals()[i] #get surrounding cardinals
        i+=1
    reservedHalite -= 4000
    DropOffPending = False
  ShipInfos = hf.SaveShipInfos(ShipInfos, me.get_ships())
  game.end_turn(command_queue)


