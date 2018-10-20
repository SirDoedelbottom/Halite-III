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
def StateMachine(state, ship):
  departure = me.shipyard == ship.position
  ShipInfos[ship.id].Priority == -1
  for do in me.get_dropoffs()
    if do.position == ship.position
      departure = true
  if departure
    ShipInfos[ship.id].Priority = 3
  if state == ShipState.north:
    if ShipInfos[ship.id].Priority == -1
      ShipInfos[ship.id].Priority = 0
    hf.SetWishPos(ship.id,ship.position.directional_offset(Direction.North), collisionMap)
  elif state == ShipState.east:
    if ShipInfos[ship.id].Priority == -1
      ShipInfos[ship.id].Priority = 0
    hf.SetWishPos(ship.id,ship.position.directional_offset(Direction.East), collisionMap)
  elif state == ShipState.south:
    if ShipInfos[ship.id].Priority == -1
      ShipInfos[ship.id].Priority = 0
    hf.SetWishPos(ship.id,ship.position.directional_offset(Direction.South), collisionMap)
  elif state == ShipState.west:
    if ShipInfos[ship.id].Priority == -1
      ShipInfos[ship.id].Priority = 0
    hf.SetWishPos(ship.id,ship.position.directional_offset(Direction.West), collisionMap)
  elif state == ShipState.returnHome:
    ShipInfos[ship.id].Priority = 2
    ShipInfos[ship.id].ReturnHome = True
    MoveQueue = hf.ShortestPath( game_map, ship.position, me.shipyard.position )
    if not MoveQueue:
      logging.info("Not returning home anymore")
      ShipInfos[ship.id].ReturnHome = False
    else:
      hf.SetWishPos(ship.id,ship.position.directional_offset(MoveQueue[0]), collisionMap)
  elif state == ShipState.harvest:
    if ShipInfos[ship.id].Priority == -1
      ShipInfos[ship.id].Priority = 1


while True:
  game.update_frame()
  me = game.me
  game_map = game.game_map
  command_queue = []
  helperfunctions.RefreshDict( ShipInfos, me.get_ships() )
  collisionMap = np.zeros((game.game_map.width,game.game_map.height,5))


  for ship in me.get_ships():
    # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
    #   Else, collect halite.
    if ship.halite_amount >= 600 or ShipInfos[ship.id].ReturnHome:  # return home!
      StateMachine(command_queue,ShipState.returnHome,ship)
    elif game_map[ship.position].halite_amount < constants.MAX_HALITE / 10:
      command_queue.append( ship.move( RndDirection ) )
    else:
      command_queue.append(ship.stay_still())
  conflicts = {}
  if(!hf.ResolveCollisionMap(collisionMap,conflicts,ShipInfos))
    for key in conflicts
    #call new decision function

  # If the game is in the first 200 turns and you have enough halite, spawn a ship.
  # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
  if len(me.get_ships())==0 and game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
    command_queue.append(me.shipyard.spawn())

  game.end_turn(command_queue)




