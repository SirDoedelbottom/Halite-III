#!/usr/bin/env python3
# Python 3.6

#import hlt
import hlt
import gc
from hlt import constants
from hlt.positionals import Direction
import random
import logging
import helperfunctions
import helperfunctions2
import ShipStateMachine

#gc.init()
""" <<<Game Begin>>> """
#game = gc.game

RndDirection = random.choice([ Direction.North, Direction.South, Direction.East, Direction.West ])


# As soon as you call "ready" function below, the 2 second per turn timer will start.
gc.game.ready("MyPythonBot")

logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

#ShipInfos={}

while True:
  gc.game.update_frame()
  me = gc.game.me
  game_map = gc.game.game_map
  command_queue = []
  helperfunctions.RefreshDict( gc.ShipInfos, me.get_ships() )
  

  for ship in me.get_ships():
    # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
    #   Else, collect halite.
    if ship.halite_amount >= 600 or gc.ShipInfos[ship.id].ReturnHome:  # return home!
      ShipStateMachine.StateMachine(gc.game, command_queue,ShipStateMachine.ShipState.returnHome,ship)
    elif game_map[ship.position].halite_amount < constants.MAX_HALITE / 10:
      command_queue.append( ship.move( RndDirection ) )
    else:
      command_queue.append(ship.stay_still())

  # If the game is in the first 200 turns and you have enough halite, spawn a ship.
  # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
  if len(me.get_ships())==0 and gc.game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
    command_queue.append(me.shipyard.spawn())

  gc.game.end_turn(command_queue)

