#!/usr/bin/env python
# -*- coding: cp1252 -*-
#

"""
// The DoTurn function is where your code goes. The PlanetWars object contains
// the state of the game, including information about all planets and fleets
// that currently exist. Inside this function, you issue orders using the
// pw.IssueOrder() function. For example, to send 10 ships from planet 3 to
// planet 8, you would say pw.IssueOrder(3, 8, 10).
//
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own. Check out the tutorials and articles on the contest website at
// http://www.ai-contest.com/resources.
"""
import operator # workaround for addition bug
from PlanetWars import PlanetWars

# Compute MinimumSpanningTree ; Source: http://healthyalgorithms.wordpress.com/2009/01/13/aco-in-python-pads-for-minimum-spanning-trees/
from UnionFind import *
def MinimumSpanningTree(G):
  """
  Return the minimum spanning tree of an undirected graph G.
  G should be represented in such a way that G[u][v] gives the
  length of edge u,v, and G[u][v] should always equal G[v][u].
  The tree is returned as a list of edges.
  """

  # Kruskal's algorithm: sort edges by weight, and add them one at a time.
  # We use Kruskal's algorithm, first because it is very simple to
  # implement once UnionFind exists, and second, because the only slow
  # part (the sort) is sped up by being built in to Python.
  subtrees = UnionFind()
  tree = []
  edges = [(G[u][v],u,v) for u in G for v in G[u]]
  edges.sort()
  for W,u,v in edges:
    if subtrees[u] != subtrees[v]:
      tree.append((u,v))
      subtrees.union(u,v)
  return tree

#Compute the number of neighbors in the MST
def numberOfNeighborsInMST(G, vertex):
  numberOfNeighbors = 0
  for u in G:
    if len(u) <> 2:
      continue
    if u[0] == vertex or u[1] == vertex:
      numberOfNeighbors += 1
  return numberOfNeighbors
  
# Compute how many fleets come to a planet
def getHowManyShipsComeToPlanet(pw, idPlanet, beforeTurn, idPlayer):
  allFleets = pw.Fleets()
  totalIncomingFleets = 0
  for fleet in allFleets:
    if fleet.DestinationPlanet() <> idPlanet or fleet.TurnsRemaining() > beforeTurn:
      continue
    if fleet.Owner() == idPlayer:
      totalIncomingFleets += fleet.NumShips()
    elif idPlayer <> 0:
      totalIncomingFleets -= fleet.NumShips()
    else:
      totalIncomingFleets += fleet.NumShips()
  return totalIncomingFleets

# Compute how many fleets come to a planet at a precise turn
def getHowManyShipsComeToPlanetAtTurn(pw, idPlanet, turnNumber, idPlayer):
  allFleets = pw.Fleets()
  totalIncomingFleets = 0
  for fleet in allFleets:
    if fleet.DestinationPlanet() <> idPlanet or fleet.TurnsRemaining() <> turnNumber:
      continue
    if fleet.Owner() == idPlayer:
      totalIncomingFleets += fleet.NumShips()
    elif idPlayer <> 0:
      totalIncomingFleets -= fleet.NumShips()
    else:
      totalIncomingFleets += fleet.NumShips()   
  return totalIncomingFleets


# Compute growth of a planet. < 0 means enemy own i, > 0 we have it, =0 planet is neutral
def getGrowth(pw, planet, beforeTurn):
  totalGrowth = 0
  if planet in pw.NeutralPlanets():
    return 0
  if planet in pw.EnemyPlanets():
    return -1 * planet.GrowthRate() * beforeTurn
  if planet in pw.MyPlanets():
    return planet.GrowthRate() * beforeTurn
  return totalGrowth


# Return the distance between idPlanet and idPlanet's closest planet
def getClosestPlanetDistance(pw, idPlanet, idPlayer):
  planets = []
  if idPlayer == 0:
    planets = pw.NeutralPlanets()
  elif idPlayer == 1:
    planets = pw.MyPlanets()
  elif idPlayer == 2:
    planets = pw.EnemyPlanets()

  distance = 9999
  idClosestPlanet = 0
  for planet in planets:
    if distance > pw.Distance(idPlanet, planet.PlanetID()):
      distance = pw.Distance(idPlanet, planet.PlanetID())
      idClosestPlanet = planet.PlanetID()
    
  return distance, idClosestPlanet

# Return the distance and IDplanetof our closest planet to idPlanet that have a bigger front score.
def closestPlanetWithSmallerFrontScore(pw, idPlanet, myPlanetsFrontScore, idPlayer):
  planets = []
  if idPlayer == 0:
    planets = pw.NeutralPlanets()
  elif idPlayer == 1:
    planets = pw.MyPlanets()
  elif idPlayer == 2:
    planets = pw.EnemyPlanets()

  distance = 9999
  idNeighborPlanet = 0
  
  for planet in planets:
    if planet.PlanetID() <> idPlanet and distance > pw.Distance(idPlanet, planet.PlanetID()) and \
       myPlanetsFrontScore[planet.PlanetID()] < myPlanetsFrontScore[idPlanet]:
      distance = pw.Distance(idPlanet, planet.PlanetID())
      idNeighborPlanet = planet.PlanetID()
  
  return distance, idNeighborPlanet

# Return idPlanet's closest planets
def getClosestPlanets(pw, idPlanet, idPlayer, minDist, maxDist):
  closestPlanets = {}
  planets = []
  if idPlayer == 0:
    planets = pw.NeutralPlanets()
  elif idPlayer == 1:
    planets = pw.MyPlanets()
  elif idPlayer == 2:
    planets = pw.EnemyPlanets()

  distance = 9999
  idClosestPlanet = 0
  for planet in planets:
    if minDist <= pw.Distance(idPlanet, planet.PlanetID()) <= maxDist:
      closestPlanets[planet] = pw.Distance(idPlanet, planet.PlanetID())
    
  return closestPlanets


# Return the first o ccurence of a code. Eg if given ""
def getFirstOccurenceOfACode(pw, predictions, code):
  count = 0
  for prediction in predictions:
    if prediction[0] == code:
      return count
    count += 1
  return count


# Return True if we're on the first turn, false if we're not.
def isItFirstTurn(pw):
  return (len(pw.MyPlanets()) == 1 and len(pw.EnemyPlanets()) == 1 and pw.MyPlanets()[0].NumShips() == 100 and pw.EnemyPlanets()[0].NumShips() == 100)


# Make a list unique: http://www.peterbe.com/plog/uniqifiers-benchmark
def unifyList(seq): 
  # not order preserving 
  set = {} 
  map(set.__setitem__, seq, []) 
  return set.keys()


def computePerimeter(pw):
  n,d,N = pw.NumPlanets(),0.0,0
  for i in range(n-1):
    for j in range(i+1,n):
      d += float(pw.Distance(i,j))
      N += 1
      d/=float(N)
      perimeter = int(d/1.5)
      #print "Computed perimeter ", perimeter, "\n"

  return perimeter

      
# Find vulnerable planets
def isEnemyPlanetVulnerable(pw, enemyPlanet, myPlanetsSpareShips):
  
  doWeAttack = False
  myAttackPlanets = {}
  perimeter = 7 # 8 TO DO : moyennes des distances
  nonNeutralPlanets = pw.MyPlanets()
  nonNeutralPlanets.extend(pw.EnemyPlanets())
  
  totalShips = enemyPlanet.NumShips() # Store the number of enemy ships - our coming ships
                                      # + their coming ships - our potentially coming ships + their potentially coming ships
                                      # (taken growthrate into account)

  totalShips += getHowManyShipsComeToPlanet(pw, enemyPlanet.PlanetID(), perimeter, 2)
  totalShips += getGrowth(pw, enemyPlanet, perimeter)
  
  for nonNeutralPlanet in pw.EnemyPlanets():
    distance = pw.Distance(nonNeutralPlanet.PlanetID(), enemyPlanet.PlanetID())
    if distance > perimeter:
      continue
    totalSendableShips = nonNeutralPlanet.NumShips() + getGrowth(pw, nonNeutralPlanet, perimeter - distance)
    totalShips += totalSendableShips
  
  for nonNeutralPlanet in pw.MyPlanets():
    distance = pw.Distance(nonNeutralPlanet.PlanetID(), enemyPlanet.PlanetID())
    if distance > perimeter:
      continue
    totalSendableShips = myPlanetsSpareShips[nonNeutralPlanet.PlanetID()] + getGrowth(pw, nonNeutralPlanet, perimeter - distance)
    totalShips -= totalSendableShips
    myAttackPlanets[nonNeutralPlanet] = myPlanetsSpareShips[nonNeutralPlanet.PlanetID()]
    if totalShips < 0:
      break
  
  doWeAttack = totalShips < 0
  
  return doWeAttack, myAttackPlanets
  


def DoTurn(pw):
  ## Game constants
  MAX_TURNS = 200
  NUMBER_OF_PREDICTED_TURNS = 20 # (We count the current turn)

  # If we don't have any planet, wait next turn...
  if len(pw.MyPlanets()) == 0:
    return

  # Check if we are in first turn
  firstTurn = isItFirstTurn(pw)


  ## Compute nonNeutralPlanetsMST
  nonNeutralPlanetsGraph = {}
  nonNeutralPlanets = pw.MyPlanets()
  nonNeutralPlanets.extend(pw.EnemyPlanets())
  for u in nonNeutralPlanets:
    nonNeutralPlanetsGraph[u.PlanetID()] = {}
    for v in nonNeutralPlanets:
      nonNeutralPlanetsGraph[u.PlanetID()][v.PlanetID()] = pw.Distance(u.PlanetID(),v.PlanetID())
  nonNeutralPlanetsMST = MinimumSpanningTree(nonNeutralPlanetsGraph)

  ## Compute myPlanetsMST
  myPlanetsGraph = {}
  myPlanets = pw.MyPlanets()
  for u in myPlanets:
    myPlanetsGraph[u.PlanetID()] = {}
    for v in myPlanets:
      myPlanetsGraph[u.PlanetID()][v.PlanetID()] = pw.Distance(u.PlanetID(),v.PlanetID())
  myPlanetsMST = MinimumSpanningTree(myPlanetsGraph)


  ## Compute enemyFrontPlanets and myFrontPlanets.
  # An enemy planet is on the front if in the MST there
  # is an edge between this enemy planet and one of our planet
  myFrontPlanets = []
  enemyFrontPlanets = []
  myPlanets = pw.MyPlanets()
  enemyPlanets = pw.EnemyPlanets()
  for u in nonNeutralPlanetsMST:
    if len(u) <> 2:
      continue
    if pw.GetPlanet(u[0]) in pw.MyPlanets() and pw.GetPlanet(u[1]) in pw.EnemyPlanets():
      myFrontPlanets.append(pw.GetPlanet(u[0]))
      enemyFrontPlanets.append(pw.GetPlanet(u[1]))
      pass
    if pw.GetPlanet(u[0]) in pw.EnemyPlanets() and pw.GetPlanet(u[1]) in pw.MyPlanets():
      myFrontPlanets.append(pw.GetPlanet(u[1]))
      enemyFrontPlanets.append(pw.GetPlanet(u[0]))
      pass
  #print len(myFrontPlanets)

  ## Compute myPlanetsFrontScore: the smaller, the closer to the front.
  myPlanetsFrontScore = {}
  my_planets = pw.MyPlanets()
  for myPlanet in my_planets:
    myPlanetsFrontScore[myPlanet.PlanetID()], nothing = getClosestPlanetDistance(pw, myPlanet.PlanetID(), 2)
    
  # Compute myPlanetsInFuture and myThreatenedPlanets
  # Create a prediction of the future for my planets:
  #  +3 means I get an enemy planet
  #  +2  I get a neutral planetplanet,
  #  +1 it's my planet,
  #  0 neutral planet,
  #  -1 enemy planet,
  #  -2 enemy get a neutral planet
  #  -3 enemy get my planet

  my_planets = pw.MyPlanets()
  myPlanetsInFuture = dict()
  myThreatenedPlanets = []
  for myPlanet in my_planets:
    predictions = []
    numShips = myPlanet.NumShips()
    playerIDWhoOwnsThePlanet = myPlanet.Owner()
    for i in range(NUMBER_OF_PREDICTED_TURNS):
      # Add new ships
      numShips += getHowManyShipsComeToPlanetAtTurn(pw, myPlanet.PlanetID(), i, 1)        
      # Check who owns now the planet
      if playerIDWhoOwnsThePlanet == 1: # We have the planet
        if numShips >= 0:
          newCode = 1
        else:
          newCode = -3
          playerIDWhoOwnsThePlanet = 2
          if (myThreatenedPlanets.count(myPlanet) == 0) :
            myThreatenedPlanets.append(myPlanet)
      elif playerIDWhoOwnsThePlanet == 2: # The enemy has the planet
        if numShips > 0:
          newCode = 3
          playerIDWhoOwnsThePlanet = 1
        else:
          newCode = -1
      predictions.append((newCode, numShips))
      # Add new ships
      if playerIDWhoOwnsThePlanet == 1:       
        numShips += myPlanet.GrowthRate()
      if playerIDWhoOwnsThePlanet == 2:
        numShips -= myPlanet.GrowthRate()
        
    myPlanetsInFuture[myPlanet.PlanetID()] = predictions

  # To avoid crash
  if len(myThreatenedPlanets) == 1 and len(pw.MyPlanets()) == 1:
    return
  if len(myThreatenedPlanets) == len(pw.MyPlanets()):
    return

  
  # Compute neutralPlanetsInFuture, neutralThreatenedPlanets and neutralWonPlanets
  # Create a prediction of the future for neutral planets:
  #  +3 means I get an enemy planet
  #  +2  I get a neutral planetplanet,
  #  +1 it's my planet,
  #  0 neutral planet,
  #  -1 enemy planet,
  #  -2 enemy get a neutral planet
  #  -3 enemy get my planet

  neutralPlanets = pw.NeutralPlanets()
  neutralPlanetsInFuture = dict()
  neutralThreatenedPlanets = []
  neutralWonPlanets = []
  for neutralPlanet in neutralPlanets:
    predictions = []
    newCode = 0
    numShips = neutralPlanet.NumShips()
    playerIDWhoOwnsThePlanet = neutralPlanet.Owner()
    for i in range(NUMBER_OF_PREDICTED_TURNS):
      if playerIDWhoOwnsThePlanet == 0: # The planet is still neutral
        numShips -= getHowManyShipsComeToPlanetAtTurn(pw, neutralPlanet.PlanetID(), i, 0)
        if numShips < 0:
          if getHowManyShipsComeToPlanetAtTurn(pw, neutralPlanet.PlanetID(), i, 1) > 0:
            numShips = abs(numShips) # Little math trick because since we get the planet, numShips should become positive again :-)
            newCode = 2
            playerIDWhoOwnsThePlanet = 1
            if (neutralWonPlanets.count(neutralPlanet) == 0):
              neutralWonPlanets.append(neutralPlanet)
          else:
            newCode = -2
            if (neutralThreatenedPlanets.count(neutralPlanet) == 0):
              neutralThreatenedPlanets.append(neutralPlanet)
            playerIDWhoOwnsThePlanet = 2
      else: # The planet is no more neutral
        numShips += getHowManyShipsComeToPlanetAtTurn(pw, neutralPlanet.PlanetID(), i, 1)
        if playerIDWhoOwnsThePlanet == 1: # We have the planet
          if numShips >= 0:
            newCode = 1
          else:
            newCode = -3
            playerIDWhoOwnsThePlanet = 2
        elif playerIDWhoOwnsThePlanet == 2: # The enemy has the planet
          if numShips >= 0:
            newCode = 3
            playerIDWhoOwnsThePlanet = 1
          else:
            newCode = -1
          
      predictions.append((newCode, numShips))
      # Add new ships
      if playerIDWhoOwnsThePlanet == 1:       
        numShips += myPlanet.GrowthRate()
      if playerIDWhoOwnsThePlanet == 2:
        numShips -= myPlanet.GrowthRate()
        
    neutralPlanetsInFuture[neutralPlanet.PlanetID()] = predictions    


  ## Compute myPlanetsSpareShips
  myPlanetsSpareShips = dict()
  my_planets = pw.MyPlanets()
  for myPlanet in my_planets:
    spareShips = 999999
    future = myPlanetsInFuture[myPlanet.PlanetID()]
    for stepInFuture in future:
      if stepInFuture[1] < spareShips:
        spareShips = stepInFuture[1]
    myPlanetsSpareShips[myPlanet.PlanetID()] = max(0, spareShips)
  #print "myPlanetsSpareShips:"
  #print myPlanetsSpareShips


  ## Defend myThreatenedPlanets
  for myThreatenedPlanet in myThreatenedPlanets:
    #print "myThreatenedPlanet:"
    #print myThreatenedPlanet.PlanetID()
    if len(pw.MyPlanets()) <= 1: # If we only have one planet, there is no front...
      continue
    timeRemaining = getFirstOccurenceOfACode(pw, myPlanetsInFuture[myThreatenedPlanet.PlanetID()], -3)
    closestPlanets = getClosestPlanets(pw, myThreatenedPlanet.PlanetID(), 1, 0, max(0, timeRemaining+1))
    shipsNeeded = getHowManyShipsComeToPlanet(pw, myThreatenedPlanet.PlanetID(), NUMBER_OF_PREDICTED_TURNS, 2) - myThreatenedPlanet.NumShips()
    #print "closestPlanets:"
    #print closestPlanets
    for helperPlanet in closestPlanets:
      if shipsNeeded < 0:
        break
      #print "helperPlanet:"
      #print helperPlanet.PlanetID()
      #print shipsNeeded      
      num_ships = max(0, min(shipsNeeded + 1, myPlanetsSpareShips[helperPlanet.PlanetID()], helperPlanet.NumShips() - 1))
      pw.IssueOrder(helperPlanet.PlanetID(), myThreatenedPlanet.PlanetID(), num_ships)
      #Impact the decrease in ships on this planet on a few variables               
      myPlanetsSpareShips[helperPlanet.PlanetID()] -= num_ships
      helperPlanet.RemoveShips(num_ships)

  if len(myThreatenedPlanets) == 1 and len(pw.MyPlanets()) == 1:
    return
    
  ## Neutral planet: see if the enemy tries to get a planet closer to us. If yes, send a few ships
  
  #print neutralThreatenedPlanets
  for neutralThreatenedPlanet in neutralThreatenedPlanets:
    distance1, idPlanet1 = getClosestPlanetDistance(pw, neutralThreatenedPlanet.PlanetID(), 1)
    distance2, idPlanet2 = getClosestPlanetDistance(pw, neutralThreatenedPlanet.PlanetID(), 2)
    if distance1 <= distance2: # We are closer: try to get the neutral planet right after the enemy arrives if we have enough ships
      #print "coucou"
      firstOccurence = getFirstOccurenceOfACode(pw, neutralPlanetsInFuture[neutralThreatenedPlanet.PlanetID()], -2)
      mySourceToGetNeutralPlanet = pw.GetPlanet(idPlanet1)
      if mySourceToGetNeutralPlanet in myThreatenedPlanets:
        continue
      #print neutralThreatenedPlanet.PlanetID()
      #print neutralPlanetsInFuture[neutralThreatenedPlanet.PlanetID()]
      #print firstOccurence
      # Send ships if we have enough ships
      num_ships = neutralThreatenedPlanet.GrowthRate() + 2 + (getHowManyShipsComeToPlanet(pw, neutralThreatenedPlanet.PlanetID(), firstOccurence + 1, 2) - neutralThreatenedPlanet.NumShips())
      if mySourceToGetNeutralPlanet.NumShips() > num_ships and distance1 - 2 < firstOccurence <  distance1: # Send ship just at the right time
        pw.IssueOrder(idPlanet1, neutralThreatenedPlanet.PlanetID(), num_ships)
      #Impact the decrease in ships on this planet on a few variables               
      myPlanetsSpareShips[mySourceToGetNeutralPlanet.PlanetID()] -= num_ships
      mySourceToGetNeutralPlanet.RemoveShips(num_ships)


  ## Target vulnerable enemy planets
  #print len(enemyFrontPlanets)
  for enemyFrontPlanet in enemyFrontPlanets:
    (doWeAttack, myAttackPlanets) = isEnemyPlanetVulnerable(pw, enemyFrontPlanet, myPlanetsSpareShips)
    if not doWeAttack:
      continue
    
    for myAttackPlanet in myAttackPlanets:
      if myAttackPlanet in myThreatenedPlanets:
        continue
      num_ships = min(myAttackPlanet.NumShips() - 1, myAttackPlanets[myAttackPlanet])
      if num_ships <= 0:
        continue
      pw.IssueOrder(myAttackPlanet.PlanetID(), enemyFrontPlanet.PlanetID(), num_ships)
      #Impact the decrease in ships on this planet on a few variables
      myPlanetsSpareShips[myAttackPlanet.PlanetID()] -= num_ships
      myAttackPlanet.RemoveShips(num_ships)


  ## Target neutral planets
  ## Find my strongest planet.
  done = False
  planetsAlreadyTargeted = []
  iteration = 5
  
  # Special case for first turn
  if firstTurn:
    my_planets = pw.MyPlanets()
    enemyPlanets = pw.EnemyPlanets()
    if len(my_planets) > 0 and len(my_planets) > 0:
      myPlanet = my_planets[0]
      enemyPlanet = enemyPlanets[0]
      if pw.Distance(myPlanet.PlanetID(), enemyPlanet.PlanetID()) < 9:
        iteration = 1

    
  for i in range(iteration):
  #while not done:
    source = -1
    source_score = -999999.0
    source_num_ships = 0
    my_planets = pw.MyPlanets()
    for p in my_planets:
      if p in myThreatenedPlanets:
        continue
      score = float(p.NumShips())
      if score > source_score:
        source_score = score
        source = p

    
    ## Find the weakest neutral planet close to my strong planet.
    dest = -1
    dest_score = -999999.0
    not_my_planets = pw.NeutralPlanets()
    

    for p in not_my_planets:
      distance2, idPlanet2 = getClosestPlanetDistance(pw, p.PlanetID(), 2)
      if (planetsAlreadyTargeted.count(p.PlanetID()) > 0) and firstTurn and distance2 > 8:
        continue
      if p in neutralWonPlanets or p in neutralThreatenedPlanets: # We've already dealt with neutral planet that are won or lost
        continue
      if (getHowManyShipsComeToPlanet(pw, p.PlanetID(), MAX_TURNS, 1) > 20):
        continue
      #distance1, idPlanet1 = getClosestPlanetDistance(pw, p.PlanetID(), 1)
      distance1 = pw.Distance(source.PlanetID(), p.PlanetID())
      distance2, idPlanet2 = getClosestPlanetDistance(pw, p.PlanetID(), 2)
      if distance1 >= distance2: #Don't attack if ennemy is closer
        continue      
      score = (1.0 + p.GrowthRate()) / (p.NumShips() + 3*pw.Distance(source.PlanetID(), p.PlanetID()))
      if score > dest_score:
        dest_score = score
        dest = p

    
    ## Send ships from my strongest planet to the target neutral planet
    if (dest_score > 0.01 and myPlanetsSpareShips[source.PlanetID()] > 1 and source <> -1 and source.PlanetID() >= 0 and source.NumShips() > 1 and dest <> -1 and dest.PlanetID() >= 0 and not(source in myThreatenedPlanets)) :
      planetsAlreadyTargeted.append(dest.PlanetID())
      num_ships = dest.NumShips() + 1
      #distance1 = pw.Distance(source.PlanetID(), dest.PlanetID())
      #distance2, idPlanet2 = getClosestPlanetDistance(pw, dest.PlanetID(), 2)
      #if firstTurn and float(distance1)/distance2 > 0.7 : # send a bit more ships if 1st turn + close to enemy
        #num_ships += int(max(0, float((distance1)/distance2 - 0.7))*20)
        #pass
      # only send ships if we can take in one attacks
      if ( num_ships > 0 and source.NumShips() > num_ships and myPlanetsSpareShips[source.PlanetID()] > num_ships):
        pw.IssueOrder(source.PlanetID(), dest.PlanetID(), num_ships)
        #Impact the decrease in ships on this planet on a few variables               
        myPlanetsSpareShips[source.PlanetID()] -= num_ships
        source.RemoveShips(num_ships)
      #print "numéro de tour:", i
    else:
      #done = True
      #print "numéro de tour break:", i
      break
      

      
  ## Fortify threaned planets
  
  ## Fortify front planets (=planets that are the closest to at least one planet enemy)
  
  # Compute myBackPlanets and frontPlanets
  myBackPlanets = pw.MyPlanets()
  #frontPlanets = list(myThreatenedPlanets)
  frontPlanets = list(myFrontPlanets)  
  
  my_planets = pw.MyPlanets()
  enemyPlanets = pw.EnemyPlanets()
  myAndEnemyPlanetsNeighbours = []
  for pEnemy in enemyPlanets:
    if len(pw.MyPlanets()) <= 1: # If we only have ona planet, there is no front...
      continue
    distance = 99999.0
    closestPlanet = None
    for p in my_planets:
      if pw.Distance(pEnemy.PlanetID(), p.PlanetID()) < distance:
        closestPlanet = p
        distance = pw.Distance(pEnemy.PlanetID(), p.PlanetID())
    if closestPlanet == None:
      continue
    #myAndEnemyPlanetsNeighbours.append([p, pEnemy])
    if frontPlanets.count(closestPlanet) < 1:
      frontPlanets.append(closestPlanet)
    if myBackPlanets.count(closestPlanet) > 0:
      myBackPlanets.remove(closestPlanet)

    #Remove from myBackPlanets all myThreatenedPlanets
    for myThreatenedPlanet in myThreatenedPlanets:
      if myBackPlanets.count(myThreatenedPlanet) > 0 :
        myBackPlanets.remove(myThreatenedPlanet)

    myFarBackPlanets = []
    # For each back planet I have, send ships to the closest front
    #TO DO: replace code by using MST + frontscore
    for pBack in myBackPlanets:
      if pBack in myThreatenedPlanets:
        continue
      distance = 99999
      # Find closest planet
      closestFrontPlanet = None
      for pFront in frontPlanets:
        if pw.Distance(pBack.PlanetID(), pFront.PlanetID()) < distance:
          closestFrontPlanet = pFront
          distance = pw.Distance(pBack.PlanetID(), pFront.PlanetID())
          
      # Send ships to the closest front     
      num_ships = int(pBack.NumShips()/2)
      num_ships = min(num_ships, myPlanetsSpareShips[pBack.PlanetID()])
      TOO_FAR = 10
      if num_ships > 0 and num_ships < pBack.NumShips() and \
         pBack.NumShips() > (-1*getHowManyShipsComeToPlanet(pw, pBack.PlanetID(), 20, 1) - getGrowth(pw, pBack, 1)) and \
         not(closestFrontPlanet == None or pBack == None):
        if distance < TOO_FAR: # Don't send ships if it's too far!
          pw.IssueOrder(pBack.PlanetID(), closestFrontPlanet.PlanetID(), num_ships)        
          myPlanetsSpareShips[pBack.PlanetID()] -= num_ships
          pBack.RemoveShips(num_ships)
        else:
          # We find our neighbor planet in the MST with smallest frontScore and send ships there
          smallestFrontScore = 9999
          smallestFrontScoreNeighborPlanet = None
          neighborPlanet = None
          for u in myPlanetsMST:
            if len(u) <> 2:
              continue
            if u[0] == pBack.PlanetID():
              neighborPlanet = pw.GetPlanet(u[1])
            elif u[1] == pBack.PlanetID():
              neighborPlanet = pw.GetPlanet(u[0])
            else:
              continue
            # To avoid risk of cycles in fortfications
            if (numberOfNeighborsInMST(myPlanetsMST, neighborPlanet.PlanetID()) <= 1): 
              #continue
              pass
            if smallestFrontScore > myPlanetsFrontScore[neighborPlanet.PlanetID()]:
              smallestFrontScore = myPlanetsFrontScore[neighborPlanet.PlanetID()]
              smallestFrontScoreNeighborPlanet = neighborPlanet

          # To avoid risk of cycles in fortfications 
          if (numberOfNeighborsInMST(myPlanetsMST, pBack.PlanetID()) <= 1) and myPlanetsFrontScore[neighborPlanet.PlanetID()] > myPlanetsFrontScore[pBack.PlanetID()] :
            dist, idNeighborPlanet = closestPlanetWithSmallerFrontScore(pw, pBack.PlanetID(), myPlanetsFrontScore, 1)
            if dist == 9999:
              continue
            smallestFrontScoreNeighborPlanet = pw.GetPlanet(idNeighborPlanet)
              
          closestNeutralPlanetDistance, closestNeutralPlanet = getClosestPlanetDistance(pw, pBack.PlanetID(), 0)
          if smallestFrontScoreNeighborPlanet <> None and (pBack.NumShips() > 80 or closestNeutralPlanetDistance > 10):    
            pw.IssueOrder(pBack.PlanetID(), smallestFrontScoreNeighborPlanet.PlanetID(), num_ships)
            #Impact the decrease in ships on this planet on a few variables               
            myPlanetsSpareShips[pBack.PlanetID()] -= num_ships
            pBack.RemoveShips(num_ships)
    
  return


def main():
  map_data = ''
  while(True):
    current_line = raw_input()
    if len(current_line) >= 2 and current_line.startswith("go"):
      pw = PlanetWars(map_data)
      DoTurn(pw)
      pw.FinishTurn()
      map_data = ''
    else:
      map_data += current_line + '\n'


if __name__ == '__main__':
  try:
    import psyco
    psyco.full()
  except ImportError:
    pass
  try:
    main()
  except KeyboardInterrupt:
    print 'ctrl-c, leaving ...'
