#!/usr/bin/env python3
# Python 3.6

import hlt
from hlt import constants
from hlt.positionals import Direction
import random
import logging
import helperfunctions as hf
import helperfunctions2
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
  departure = me.shipyard == ship.position
  ShipInfos[ship.id].Priority = -1
  wishDirection = Direction.Still
  for do in me.get_dropoffs():
    if do.position == ship.position:
      departure = True

  if departure:
    ShipInfos[ship.id].Priority = 3
    logging.info("Not returning home anymore")
    ShipInfos[ship.id].ReturnHome = False


  if ship.halite_amount >= 900 or ShipInfos[ship.id].ReturnHome:  # return home!
    ShipInfos[ship.id].Priority = 2
    wishDirection = hf.FindCheapestShortestRoute( game_map, ship.position, me.shipyard.position,blocked )
    hf.SetWishPos(ship.id,ship.position.directional_offset(wishDirection), collisionMap)
    ShipInfos[ship.id].ReturnHome = True
  else:
    wishSpot = hf.FindClosestValidSpot(game_map,ship.position,15,blocked)
    wishDirection = hf.FindCheapestShortestRoute(game_map,ship.position,wishSpot,blocked)
    if ShipInfos[ship.id].Priority == -1:
      if wishDirection == Direction.Still:
        ShipInfos[ship.id].Priority = 1 
      else:
        ShipInfos[ship.id].Priority = 0
    hf.SetWishPos(ship.id,ship.position.directional_offset(wishDirection), collisionMap)
  ShipInfos[ship.id].Direction = wishDirection

""" <<<Game Loop>>> """

while True:
  game.update_frame()

  logging.info(game)

  me = game.me
  game_map = game.game_map
  command_queue = []
  hf.RefreshDict( ShipInfos, me.get_ships() )
  collisionMap = np.zeros((game.game_map.width,game.game_map.height,5))


  for ship in me.get_ships():
    whatDo(ship)
  conflicts = {}
  if hf.ResolveCollisionMap(collisionMap,conflicts,ShipInfos):
    for key in conflicts:
      whatDo(me.ge(key),conflicts[key])
  else:
      for ship in me.get_ships():
        command_queue.append(ship.MoveDirection(ShipInfos[ship.id].Direction))

  # If the game is in the first 200 turns and you have enough halite, spawn a ship.
  # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
  if game.turn_number <= 300 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied and collisionMap[me.position.x][me.position.x][0]==0:
    command_queue.append(me.shipyard.spawn())

  game.end_turn(command_queue)




