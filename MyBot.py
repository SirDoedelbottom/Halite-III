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


RndDirection = random.choice([ Direction.North, Direction.South, Direction.East, Direction.West ])


# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("MyPythonBot")
ShipInfos={}
ShipState = Enum('ShipState', 'north east south west returnHome harvest')


logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """
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

  if ship.halite_amount < np.ceil(game_map[ship.position].halite_amount/10):
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
  if game.turn_number <= 300 and me.halite_amount >= constants.SHIP_COST and collisionMap[me.shipyard.position.x][me.shipyard.position.y][0]==-1:
    command_queue.append(me.shipyard.spawn())

  game.end_turn(command_queue)


