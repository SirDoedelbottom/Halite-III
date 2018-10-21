#!/usr/bin/env python3
# Python 3.6

import hlt
from hlt import constants
from hlt.positionals import Direction
from hlt.positionals import Position
import random
import logging
import helperfunctions as hf
import numpy as np
from enum import Enum     # for enum34, or the stdlib version


game = hlt.Game()

""" <<<Game Begin>>> """



# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("MyPythonBot")
ShipInfos={}
ShipState = Enum('ShipState', 'north east south west returnHome harvest')


logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """
def EvaluatePoint(position):
  maxDist = 5
  positionValue = game_map[position].halite_amount
  for dist in range(1,maxDist):
    for i in range(dist):
      positionValue+= int(game_map[game_map.normalize(Position(position.x+i,position.y-dist+i))].halite_amount * (1 - i/(dist+1)))
      positionValue+= int(game_map[game_map.normalize(Position(position.x+dist-i,position.y+i))].halite_amount * (1 - i/(dist+1)))
      positionValue+= int(game_map[game_map.normalize(Position(position.x-i,position.y+dist-i))].halite_amount * (1 - i/(dist+1)))
      positionValue+= int(game_map[game_map.normalize(Position(position.x-dist+i,position.y-i))].halite_amount * (1 - i/(dist+1)))
  return positionValue

def EvaluateMap():
  evaluatedMap = np.zeros([game_map.width,game_map.height])
  for x in range(game_map.width):
    for y in range(game_map.height):
      evaluatedMap[x,y] = EvaluatePoint(Position(x,y))
  return evaluatedMap

  
def whatDo(ship, blocked = []):
  departure = me.shipyard.position == ship.position
  ShipInfos[ship.id].Priority = -1
  wishDirection = Direction.Still
  for do in me.get_dropoffs():
    if do.position == ship.position:
      departure = True

  if departure:
    ShipInfos[ship.id].Priority = 3
    ShipInfos[ship.id].ReturnHome = False

  if RushHome:
    # find closest Spot to home:
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
    if ship.position in BestRetSpot.get_surrounding_cardinals():
      wishDirection = game_map.get_unsafe_moves(ship.position, BestRetSpot)[0]
      logging.info(ShipInfos[ship.id].Direction)
    else: # not in surrounding cardinals => navigate to BestRetSpot
      ShipInfos[ship.id].Priority = 2
      wishDirection = hf.FindCheapestShortestRoute( game_map, ship.position, BestRetSpot, blocked )
      hf.SetWishPos(ship.id,game_map.normalize(ship.position.directional_offset(wishDirection)), collisionMap)
  elif ship.halite_amount < np.ceil(game_map[ship.position].halite_amount/10):
    ShipInfos[ship.id].Priority = 4
    hf.SetWishPos(ship.id,ship.position, collisionMap)
  elif ship.halite_amount >= 900 or ShipInfos[ship.id].ReturnHome:  # return home!
    ShipInfos[ship.id].Priority = 2
    wishDirection = hf.FindCheapestShortestRoute( game_map, ship.position, me.shipyard.position,blocked )
    hf.SetWishPos(ship.id,game_map.normalize(ship.position.directional_offset(wishDirection)), collisionMap)
    ShipInfos[ship.id].ReturnHome = True
  else:
    wishSpot = hf.FindClosestValidSpot(game_map,ship.position,10,blocked)
    wishDirection = hf.FindCheapestShortestRoute(game_map,ship.position,wishSpot,blocked)
    if ShipInfos[ship.id].Priority == -1:
      if wishDirection == Direction.Still:
        ShipInfos[ship.id].Priority = 1 
      else:
        ShipInfos[ship.id].Priority = 0
    hf.SetWishPos(ship.id,game_map.normalize(ship.position.directional_offset(wishDirection)), collisionMap)
  ShipInfos[ship.id].Direction = wishDirection

""" <<<Game Loop>>> """

while True:
  game.update_frame()


  me = game.me
  game_map = game.game_map
  command_queue = []
  hf.RefreshDict( ShipInfos, me.get_ships() )
  collisionMap = np.ones((game.game_map.width,game.game_map.height,5))
  collisionMap = -collisionMap
  RushHome = False
  ShipDistList = []
  for ship in me.get_ships():
    DistToHome = game_map.calculate_distance(me.shipyard.position, ship.position)
    for DropOff in me.get_dropoffs():
      DistToDropoff = game_map.calculate_distance(DropOff.position, ship.position)
      if DistToDropoff < DistToHome:
        DistToHome = DistToDropoff
    ShipDistList.append( (ship.id, DistToHome) )
  ShipDistList.sort(key=lambda tup: tup[1])
  MaxDistShips = 0
  logging.info("Ships with their Distance to Home:" + str(ShipDistList))
  if len(ShipDistList) != 0:
    MaxDist = ShipDistList[-1][1]
  else:
    MaxDist = 0
  for ShipDist in ShipDistList:
    if ShipDist[1] ==  ShipDistList[-1][1]:
      MaxDistShips += 1
  logging.info("Number of Ships on Max Distance:" + str(MaxDistShips))
  if (constants.MAX_TURNS - game.turn_number) - (MaxDist+MaxDistShips) <= 0: # safty Distance 
    logging.info("Max Turns = "+str(constants.MAX_TURNS) + ", Turn Number = " + str(game.turn_number) + ", START THE RUSH!!!")
    RushHome = True

  for ship in me.get_ships():
    whatDo(ship)
  conflicts = {}
  counter = 10
  while hf.ResolveCollisionMap(collisionMap,conflicts,ShipInfos):
    counter -= 1
    if counter == 0:
      logging.info("can't resolve conflicts: " + str(conflicts))
      break
    for key in conflicts:
      whatDo(me.get_ship(key),conflicts[key])
  for ship in me.get_ships():
    logging.info("ShipInfo: " + str(ship.id)+ " : " + str(ShipInfos[ship.id].Direction))
    command_queue.append(ship.move(ShipInfos[ship.id].Direction))

  # If the game is in the first 200 turns and you have enough halite, spawn a ship.
  # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
  if game.turn_number <= constants.MAX_TURNS*3/5 and me.halite_amount >= constants.SHIP_COST and collisionMap[me.shipyard.position.x][me.shipyard.position.y][0]==-1:
    command_queue.append(me.shipyard.spawn())

  game.end_turn(command_queue)


