#!/usr/bin/env python3
# Python 3.6
import hlt
from hlt import constants
from hlt.positionals import Direction
import random
import logging

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

def RefreshDict( Dict, hltShips ):
  for ship in hltShips:
    if ship.id not in Dict:
      #append ShipInfo to dict:
      Dict[ship.id]=ShipInfo()


def FindClosestValidSpot( game_map, ShipPos, max_dist, InvalidSpots = [], threshold = 100 ):
  """ Returns the position of the closest valid spot (not blocked, enough halite avaliable) within the given range """
  BestSpot = ShipPos                  # default: stay still
  for dist in range(1, max_dist):     # iterate over distances
    # get Spots with this range
    Spots = []
    for i in range(dist):
      Spots.append( ShipPos.directional_offset( (i,dist-i) ) )
      Spots.append( ShipPos.directional_offset( (-i,-dist+i) ) )
    # check Halite threshold on Spots
    max_amount = -1
    for Spot in Spots:
      if game_map[game_map.normalize(Spot)].halite_amount >= max(threshold,max_amount) and Spot not in InvalidSpots:
        BestSpot = Spot
        max_amount = game_map[game_map.normalize(Spot)].halite_amount
    if BestSpot != ShipPos:
      break
  return BestSpot

def FindCheapestShortestRoute( game_map, ShipPos, DestPos, InvalidSpots = [] ):
  """ Find the Cheapest Route, but only out of the shortest Routes. (Don't even consider non-shortest Routes) """
  # define rectangle from Start to Destination:
  diffX = DestPos.x - ShipPos.x
  diffY = DestPos.y - ShipPos.y
  if abs(diffX - game_map.width) < abs(diffX):
    diffX -= game_map.width
  if abs(diffY - game_map.height) < abs(diffY):
    diffY -= game_map.height
  for dist in range(1, calculate_distance(ShipPos, DestPos)):
    # evaluate all Spots with dist and possibly add to "to_process_list"
    