#!/usr/bin/env python3
# Python 3.6

#import hlt
import hlt
from hlt import constants
from hlt.positionals import Direction
import random
import logging
import helperfunctions
import helperfunctions2
from enum import Enum     # for enum34, or the stdlib version


game = hlt.Game()

""" <<<Game Begin>>> """


RndDirection = random.choice([ Direction.North, Direction.South, Direction.East, Direction.West ])


# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("MyPythonBot")
ShipInfos={}
ShipState = Enum('ShipState', 'north east south west returnHome harvest')


logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

#ShipInfos={}
def StateMachine(CQueue, state, ship):
  if state == ShipState.north:
    map_cell.mark_unsafe(ship)
    game_map.naive_navigate(ship, destination)
    CQueue.append( ship.move(Direction.North))
    pass
  elif state == ShipState.east:
    CQueue.append( ship.move(Direction.East))
    pass
  elif state == ShipState.south:
    CQueue.append( ship.move(Direction.South))
    pass
  elif state == ShipState.west:
    CQueue.append( ship.move(Direction.West))
    pass
  elif state == ShipState.returnHome:
    ShipInfos[ship.id].ReturnHome = True
    MoveQueue = helperfunctions.ShortestPath( game_map, ship.position, me.shipyard.position )
    if not MoveQueue:
      logging.info("Not returning home anymore")
      ShipInfos[ship.id].ReturnHome = False
    else:
      CQueue.append( ship.move( MoveQueue[0] ))
  elif state == ShipState.harvest:
    pass


""" <<<Game Loop>>> """

while True:
  game.update_frame()

  logging.info(game)

  me = game.me
  game_map = game.game_map
  command_queue = []
  helperfunctions.RefreshDict( ShipInfos, me.get_ships() )
  

  for ship in me.get_ships():
    # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
    #   Else, collect halite.
    if ship.halite_amount >= 600 or ShipInfos[ship.id].ReturnHome:  # return home!
      StateMachine(command_queue,ShipState.returnHome,ship)
    elif game_map[ship.position].halite_amount < constants.MAX_HALITE / 10:
      command_queue.append( ship.move( RndDirection ) )
    else:
      command_queue.append(ship.stay_still())

  # If the game is in the first 200 turns and you have enough halite, spawn a ship.
  # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
  if len(me.get_ships())==0 and game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
    command_queue.append(me.shipyard.spawn())

  game.end_turn(command_queue)




