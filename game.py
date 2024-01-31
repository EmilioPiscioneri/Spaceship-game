thisFolder = "/python-programming/Spaceship game/"
import pygame # pygame renderer for 2D
import math
import numpy # for tuple math
import time
import random

def getCurrentMillisecondTime():
    return round(time.time() * 1000)

# Angles are in radians, rotation is counter-clockwise and done around origin (0,0)
# https://stackoverflow.com/questions/2259476/rotating-a-point-about-another-point-2d
def rotate2DVector(vectorToRotate : tuple, angle) -> tuple:
    oldX = vectorToRotate[0]
    oldY = vectorToRotate[1]
    newCoord = (oldX * math.cos(angle) - oldY * math.sin(angle),
                oldX * math.sin(angle) + oldY * math.cos(angle))
    
    return newCoord

# Takes in two 2D tuples (x,y). Angles are in radians, rotation is counter-clockwise
def rotate2DVectorAroundPoint(vectorToRotate : tuple, pointToRotateAround : tuple, angle : float) -> tuple:
    #Subtract pivot point
    noPoint = numpy.subtract(vectorToRotate, pointToRotateAround)

    #Rotate vector
    rotatedNoPoint = rotate2DVector(noPoint,angle)

    # add back pivot
    finalPoint = numpy.add(rotatedNoPoint, pointToRotateAround)

    return finalPoint

# Create Direction emnum
class Direction(): 
    north = 1 # up
    south = 2 # down
    west = 3 # left
    east = 4 # right 
    northWest = 5
    northEast = 6
    southWest = 7
    southEast = 8
    none = 9

    # Returns an int
    @staticmethod
    def getOppositeDirection(inputDirecion : int) -> int:
        if(type(inputDirecion) != int):
            raise Exception("ERROR: invalid arg Direction, not an int")
        
        if(inputDirecion == Direction.north):
            return Direction.south
        elif(inputDirecion == Direction.south):
            return Direction.north
        elif(inputDirecion == Direction.west):
            return Direction.east
        elif(inputDirecion == Direction.east):
            return Direction.west
        elif(inputDirecion == Direction.northWest):
            return Direction.southEast
        elif(inputDirecion == Direction.northEast):
            return Direction.southWest
        elif(inputDirecion == Direction.southEast):
            return Direction.northWest
        elif(inputDirecion == Direction.southWest):
            return Direction.northEast
        
    # Returns a string
    @staticmethod
    def DirectionToString(inputDirecion : int) -> str:
        if(type(inputDirecion) != int):
            raise Exception("ERROR: invalid arg Direction, not an int")
        if(inputDirecion == Direction.north):
            return "north"
        elif(inputDirecion == Direction.south):
            return "south"
        elif(inputDirecion == Direction.west):
            return "west"
        elif(inputDirecion == Direction.east):
            return "east"
        elif(inputDirecion == Direction.northWest):
            return "north-west"
        elif(inputDirecion == Direction.northEast):
            return"north-east"
        elif(inputDirecion == Direction.southEast):
            return "south-east"
        elif(inputDirecion == Direction.southWest):
            return "south-west"
        elif(inputDirecion == Direction.none):
            return "none"

# make controls enum
class Controls():
    WASD = 1
    #arrowKeys = 2

pygame.init()
screenSize = 719 # will be two sets of screen size, a square
screen = pygame.display.set_mode((screenSize, screenSize)) # screen is a surface
clock = pygame.time.Clock()
running = True
movePlayerDelay = 100 # how many milliseconds between each player move  

class GameController():
    level = 1 # what level the game is on. Start at 1 
    end = False # end the game bool
    endReason : str = "" # Reason for ending
    gameEndedTextFontSize = 64
    gameMap : object = None
    screen : pygame.surface.Surface = None
    player = None # player
    enemyController = None

    def __init__(self, gameMap : object, screen : pygame.surface.Surface) -> None:
        self.gameMap = gameMap
        self.screen = screen
        self.player = player
        self.enemyController = enemyController

    # Ends a game
    def EndGame(self, reason : str):
        self.end = True # Stops certaining things from updating and rendering
        self.endReason = reason

    # Renders the end game text and reason
    def RenderEndGame(self) -> None:
        screen = self.screen
        screenSizeXY : tuple = screen.get_size()
        # Render dark screen with alpha
        alphaSurface = pygame.Surface((screenSizeXY[0], screenSizeXY[1])) # width and height must be a tuple
        alphaSurface.fill((16,16,16))
        alphaSurface.set_alpha(18) # set alpha, int from 0-255
        screen.blit(alphaSurface, (0,0)) # render at (0,0)

        # Display game ended text
        gameEndedText = "Game over"
        gameEndedTextFontSize = self.gameEndedTextFontSize
        gameEndedTextObject = pygame.font.SysFont("Arial Nova", gameEndedTextFontSize)
        gameEndedTextSurface = gameEndedTextObject.render(gameEndedText, True, (221, 50, 50))
        gameEndedTextSize = gameEndedTextSurface.get_size()
        
        gameEndedTextlocation = (screenSizeXY[0] / 2 - gameEndedTextSize[0] / 2,screenSizeXY[1] / 2 - gameEndedTextSize[1] / 2) # Centred in middle of screen
        # Display game ended reason text
        gameEndedReasonText = self.endReason
        gameEndedReasonFontSize = 16
        gameEndedReasonObject = pygame.font.SysFont("Arial Nova", gameEndedReasonFontSize)
        gameEndedReasonSurface = gameEndedReasonObject.render(gameEndedReasonText, True, (207, 55, 55))
        gameEndedReasonSize = gameEndedReasonSurface.get_size()
        gameEndedReasonlocation = (screenSizeXY[0] / 2 - gameEndedReasonSize[0] / 2, gameEndedTextlocation[1] + gameEndedTextSurface.get_height() + 10) # Centred in middle of screen on x and y of game Ended text + padding

        screen.blit(gameEndedTextSurface, gameEndedTextlocation) # render text to screen
        screen.blit(gameEndedReasonSurface, gameEndedReasonlocation) # render text to screen

# Divide map into invisible GameMap. Each segment of GameMap is a tile.
# Has its own coordinate system. E.g. (1,2) will be second tile on x and third tile on y start from bottom-left. Only positive values go from, note: this means range(0, 9) inlusive, on x, is 10
# (-1 to -10) on x is 10. Same applies to Y
class GameMap():

    errorOnCreation = False
    tileSize: int = 0 # An int. Tile size of x and y for each tile should be square
    rows = 0 # How many rows there are
    rowSize = 0 # How many tiles there are, per row
    rowsUpdated = True # changed to True whenever row count is changed. Start as True to get initial rows
    

    #when GameMap gets intiated. -> [type] is the return. : [type] gives a hint of parameter type
    def __init__(self, tileSize: int) -> None:
        #type check
        if (type(tileSize) != int):
            print("ERROR: tile size is not an int")
            self.errorOnCreation = True
            return None
        
        self.tileSize = tileSize # Set the til size.

    #Updates how many rows are possible
    def UpdateRows(self, screenSizeX : int, screenSizeY : int):
        if(self.rowsUpdated == True):
            self.rowSize = screenSizeX // self.tileSize
            self.rows = screenSizeY // self.tileSize # do a simple floor division
        

    # returns tile coordinates which real coordihnates are in. Must be a tuple
    @staticmethod
    def realToTileCoords(realCoords : tuple, tileSize: int) -> tuple:
         #type check
       if (type(realCoords) != tuple):
           raise Exception("ERROR: realCoords is not a tuple")
        
        # // is floor divison. This means the result pf the division is rounded down to nearest whole number always.
        # do floor for positive numbers and ceil for negative 
        # do tilesize + 1 becuase it needs to from -1 to -tileSize -1
       tileCoords : tuple = (0,0) # default to 0,0

       if realCoords[0] < 0: # x negative
           tileCoords = (math.ceil(realCoords[0] / (tileSize)), realCoords[1])
       if realCoords[0] > 0: # x positive
           tileCoords = (realCoords[0] // tileSize, realCoords[1])
       if realCoords[1] < 0: # y negative
           tileCoords = (tileCoords[0], math.ceil(realCoords[1] / (tileSize)))
       elif realCoords[1] > 0: # y positive
           tileCoords = (tileCoords[0], realCoords[1] // tileSize)

       return tileCoords

    # Returns tile coords converted to real
    @staticmethod
    def tileCoordsToReal(tileCoord : tuple, tileSize: int) ->tuple:
       if (type(tileCoord) != tuple):
           raise Exception("ERROR: tileCoord is not a tuple")
       
       realCoord : tuple = (0,0) # initiate

       if(tileCoord[0] < 0): # x negative
           realCoord = (tileCoord[0] * tileSize, realCoord[1])
       elif(tileCoord[0] > 0): # x positive
           realCoord = (tileCoord[0] * tileSize - 1, tileCoord[1])
			 
       if(tileCoord[1] < 0): # y negative
           realCoord = (realCoord[0],tileCoord[1] * tileSize)
       elif(tileCoord[1] > 0): # y positive
           realCoord =  (realCoord[0], tileCoord[1] * tileSize - 1)

       return realCoord
        
# Player is rendered as triangle
class PlayerController():
    size : tuple = (5,15) # tuple of real coords, first value is width between base and second is height
    playerPosition : tuple = None # the positions of the player, starting from bottom-left
    currentDirection : int = Direction.none # the current Direction of snake, as int. Default to up
    colour = (116, 149, 189)
    screen : pygame.surface = None # initalise
    gameMap : GameController = None # initialise
    killsTextPadding = (10,10) # Padding pixels from top-left to give tjhe length text
    killsTextFontSize = 32 # font size of the length text
    playerSpeed : int = 10 # how many pixels the player moves per frame
    colour = (255,255,255) # The colour of the player
    kills = 0 # how many total kills the player has
    hitbox : pygame.rect = None # just a rect, does not hold the render. Updated on .Render()
    hitboxColour = (151, 236, 239) # For debugging
    #hitboxOutlineSize = 3 # For debugging, width of outline in pixels
    hp = 300 # health
    directionBeforeRest : int = None # intended to be set before direction.none is made current direction

    # constrcutor must have screen and GameMap and tilesiaze arg
    def __init__(self,screen : pygame.surface, game : GameController, tileSize : int ) -> None:
        # -- Start location

        #floor the / 2 because it avoids decimals 
        startLocation = (screenSize // 2, screenSize // 2) # make starting pos the middle
        if (startLocation[0] > 0 and startLocation[0] % 2 == 0 ): # if even and positive on x
            startLocation = (startLocation[0] - self.size[0]//2, startLocation[1]) # same location - width on x
        if (startLocation[1] > 0 and startLocation[1] % 2 == 0 ): # if even and positive on y
            startLocation = (startLocation[0],startLocation[1] - self.size[1]//2) # same location - height on y
        self.playerPosition = startLocation # set it is start
        self.gameMap = game.gameMap
        width = self.size[0]
        height = self.size[1]
        hitbox = pygame.Rect(startLocation[0], startLocation[1] - height, width, height) # do - height because canvas is top left based
        self.hitbox = hitbox
        # -- More init
        self.tileSize = tileSize
        self.screen = screen
        self.game = game
        game.player = self # set player

    # takes in real coords of a positio n
    def IsOutOfScreenBounds(self , desiredPosition : tuple) -> bool:
        screenSize = screen.get_size()
        return (desiredPosition[0] < 0 or desiredPosition[0] > screenSize[0] or desiredPosition[1] < 0 or desiredPosition[1] > screenSize[1])

    # returns real coords of a move in direction if it were to happen
    def getSimulatedMoveInDirection(self,moveDirection : int) -> tuple:
        lastPlayerPosition : tuple = self.playerPosition
        playerSpeed : int = self.playerSpeed # how many pixels per movement
        newPlayerPos : tuple = lastPlayerPosition

        if(moveDirection == Direction.north): # moved up
            newPlayerPos = (lastPlayerPosition[0], lastPlayerPosition[1] - playerSpeed)
        elif(moveDirection == Direction.south): # moved down
            newPlayerPos = (lastPlayerPosition[0], lastPlayerPosition[1] + playerSpeed)
        elif(moveDirection == Direction.east): # moved right
            newPlayerPos = (lastPlayerPosition[0] + playerSpeed, lastPlayerPosition[1])
        elif(moveDirection == Direction.west): # moved left
            newPlayerPos = (lastPlayerPosition[0] - playerSpeed, lastPlayerPosition[1])
            # Diagonal direction. 
        elif(moveDirection == Direction.northWest): # moved up-left
            newPlayerPos = numpy.add(lastPlayerPosition, (-1 * playerSpeed,-1 * playerSpeed))
        elif(moveDirection == Direction.northEast): # moved up-right
            newPlayerPos = numpy.add(lastPlayerPosition, (playerSpeed,-1 * playerSpeed))
        elif(moveDirection == Direction.southEast): # moved down right
            newPlayerPos = numpy.add(lastPlayerPosition, (playerSpeed,playerSpeed))
        elif(moveDirection == Direction.southWest): # moved down left
            newPlayerPos = numpy.add(lastPlayerPosition, (-1*playerSpeed,playerSpeed))

        return newPlayerPos # return new pos 


    # move the player in self.currentDirection 
    def MoveInCurrentDirection(self) -> None:
        currentDirection = self.currentDirection
        newPosition = self.getSimulatedMoveInDirection(currentDirection)
        # screenSize = screen.get_size()
        
        if(not self.IsOutOfScreenBounds(newPosition)):
            self.playerPosition = newPosition # set new pos 

    # must be called each frame, displays the character
    def Render(self) -> None:
        #print("rendering")
        #pygame.draw.rect(screen, self.colour, pygame.Rect(0,0,100,100))
        # type check
        screen = self.screen
        tileSize = gameMap.tileSize
        if (type(screen) != pygame.surface.Surface):
            raise Exception("ERROR: didn't pass a valid screen arg")
        if (type(tileSize) != int):
            raise Exception("ERROR: didn't pass a valid tileSize arg")
        playerPosition = self.playerPosition # position of player
        colour = self.colour # colour of player
        playerDirection = self.currentDirection
        if(playerDirection == Direction.none and self.directionBeforeRest != None):
            playerDirection = self.directionBeforeRest # set it to direction before stop

        playerWidth = self.size[0]
        playerHeight = self.size[1]
        

        playerPoints = [] # list of real coords
        playerPoints.append((playerPosition)) # start at bottom-left
        playerPoints.append((playerPosition[0] + playerWidth, playerPosition[1])) # create bottom-right
        playerPoints.append((playerPosition[0] + playerWidth/2,playerPosition[1]-playerHeight)) # create top
        midPoint = (playerPosition[0] + playerWidth / 2, playerPosition[1] - playerHeight / 2) # centre of triangle

        playerDirectionAngle = 0 # default or pointing North. In degrees cos they're easier to read

        # No Need to do north. Keep in mind the angle is is counter-clockwise
        if(playerDirection == Direction.east):
            playerDirectionAngle = 90
        elif(playerDirection == Direction.south):
            playerDirectionAngle = 180
        elif(playerDirection == Direction.west):
            playerDirectionAngle = 270
        elif(playerDirection == Direction.northEast):
            playerDirectionAngle = 45
        elif(playerDirection == Direction.northWest):
            playerDirectionAngle = 315 # 270 + 45
        elif(playerDirection == Direction.southEast):
            playerDirectionAngle = 135 # 180 - 45
        elif(playerDirection == Direction.southWest):
            playerDirectionAngle = 225 # 180 + 45
        
        #if not 0
        if(playerDirectionAngle != 0):
            # convert direction angle to radians
            playerDirectionAngle = math.radians(playerDirectionAngle)

            # iterate through player points
            for playerPointIndex in range(0,len(playerPoints)):
                playerPoint = playerPoints[playerPointIndex] # Get point
                playerPointRotated : tuple = rotate2DVectorAroundPoint(playerPoint, midPoint, playerDirectionAngle)

                playerPointRounded : tuple = ((round(playerPointRotated[0]), round(playerPointRotated[1])))

                playerPoints[playerPointIndex] = playerPointRounded

        # update hitbox
        
        # get left-most X and lowest Y. Lowest Y because smaller Y means higher.
        # highest x and y is used for size
        leftMostX = None # intialise
        rightMostX = None # initialise
        lowestY = None # initialise
        highestY = None # initialise

        #index = 0
        for point in playerPoints:
            #initialise x
            if leftMostX == None:
                leftMostX = point[0]
            if rightMostX  == None:
                rightMostX = 0
            #initialise y
            if lowestY == None:
                lowestY = point[1] 
            if highestY == None:
                highestY = 0
            # if point x less than existing point and y is higher
            
            
            if (point[0] < leftMostX):
                leftMostX = point[0]
            if (point[0] > rightMostX):
                rightMostX = point[0]
            if (point[1] < lowestY):
                lowestY = point[1] # set as new point, new one fouund
            if (point[1] > highestY):
                highestY = point[1]
            #index += 1
        
        # update hitbox rect
        #print(leftAndHighestMostPoint)
        
        hitboxSize = (rightMostX - leftMostX, highestY - lowestY)

        """
        # Debuggin stuff
        print("-------")
        print("Player pos:")
        print(playerPosition)
        print("Hitbox size: ")
        print(hitboxSize)
        print("Hitbox position: ")
        print((leftMostX, lowestY))
        print("Right most x and highest y")
        print("("+str(rightMostX)+", "+str(highestY)+")")
        print("Spaceship points")
        print(playerPoints)
        """
        
        self.hitbox = pygame.Rect(leftMostX, lowestY, hitboxSize[0],hitboxSize[1])
        
        #print(playerPoints)
        pygame.draw.polygon(screen, colour, playerPoints)

    # for debugging purposes
    def RenderHitbox(self) -> None:
        screen = self.screen
        hitbox = self.hitbox # a rect
        hitboxColour = self.hitboxColour

        pygame.draw.rect(screen, hitboxColour, hitbox)
            
    # renders text on top-left
    def RenderKillsText(self) -> None:
        killsTextFontSize = self.killsTextFontSize
        killsText = "Kills: "+str(self.kills) # string text to render
        killsTextObject = pygame.font.SysFont("Arial Nova",killsTextFontSize)
        killsTextSurface = killsTextObject.render(killsText, True, "white")
        padding = self.killsTextPadding
        killsTextlocation = (padding[0],padding[1]) # top left (0,0) + padding. (0,0) can be omitted
        self.screen.blit(killsTextSurface, killsTextlocation) # render text to screen
        

        
    lastDirectionChangeTime = 0 # in millis
    # changes snake Direction
    def ChangeDirection(self, moveDirection : int) -> None:
        # type check
        if(type(moveDirection) != int):
            raise Exception("ERROR: Didn't pass in an int")
        
        # save the old direction
        oldDirection = self.currentDirection
        print("Old direction: "+Direction.DirectionToString(oldDirection))
        if(moveDirection == Direction.none):
            self.directionBeforeRest = self.currentDirection

        # move snake
        # print(Direction.DirectionToString(Direction.getOppositeDirection(self.currentDirection)))
        # print(Direction.DirectionToString(moveDirection))
        self.currentDirection = moveDirection
            
    #convert real coords of pos to tile
    def GetPositionAsTile(self) -> tuple:
        return GameMap.realToTileCoords(self.playerPosition, self.gameMap.tileSize)

    lastMoveTime = 0 # in millis

    # returns True if success, does not render. Intended to be called each frame
    def Update(self) -> bool:#, render = True, screen : pygame.surface = None, tileSize : int = None):

        # Check if enough time has passed
        currentTimeInMilliseconds = getCurrentMillisecondTime()
        timeDifferenceInMillis = currentTimeInMilliseconds - self.lastMoveTime # time diifference netween current and last move in milliseconds
        if((timeDifferenceInMillis <= movePlayerDelay) or (self.lastMoveTime > 0 and timeDifferenceInMillis <= movePlayerDelay)):
            # print("WARN: not enough time has passed between player movements, skipping. Time difference is " + str(timeDifferenceInMillis)+" and delay is "+ str(moveSnakeDelay))
            return
        # now assign last move time to new move time
        self.lastMoveTime = currentTimeInMilliseconds

        # the Direction the player is facing
        
        # Move the snake
        self.MoveInCurrentDirection()

        return True
    
# Spawn enemies and control them
class EnemyController():
    lastLevelLoaded = 0 # the last level with enemies that is loaded
    game : GameController = None
    maxEnemiesPerlevel = 8
    enemyPositions = []
    player : PlayerController = None
    sizeXY : int = 15 # size of a single enemy
    enemyColour = (252, 29, 54)
    enemiesLeft = 1 # start

    def __init__(self, game : GameController, player : PlayerController) -> None:
        self.game = game
        self.player = player
        self.game.enemyController = self # set enemy controller

    # Spawmn a singular enemy
    def SpawnEnemy(self, enemyPosition):
        realTilePosition = GameMap.tileCoordsToReal(enemyPosition, self.game.gameMap.tileSize)
        self.enemyPositions.append(realTilePosition)
    
    """
    # get a rect of potential enemy location as tile coords
    def GetEnemyTileRect(self, realPosition) -> tuple:
        return GameMap.realToTileCoords(realPosition, self.game.gameMap.tileSize)
    """
        
    # get a list of all enemy locations as tile coords not using self.enemyPositions
    def GetTilesEnemyIsIn(self, realTilePositions : list) -> list:
        enemyTiles = []
        sizeXY = self.sizeXY
        gameMap = self.game.gameMap
        tileSizeXY = gameMap.tileSize
        for enemyPosition in realTilePositions:
            enemyPosition = GameMap.realToTileCoords(enemyPosition, tileCoord)
            for sizeIndexX in range(0, sizeXY):
                for sizeIndexY in range(0, sizeXY):
                    realCoord = numpy.add((sizeIndexX,sizeIndexY), enemyPosition) # add the iterated size to actual position or else it will revolve around
                    tileCoord = GameController.realToTileCoords(realCoord, tileSizeXY)
                    # tile coord doesn't exist
                    if(not(tileCoord in enemyTiles)):
                        enemyTiles.append(tileCoord)


            
            #enemyRects.append(pygame.Rect(position[0],-1 * position[1], sizeXY,sizeXY))
        return enemyTiles
    

    def GenerateEnemies(self, qtyToGenerate):
        qtyToGenerate = round(qtyToGenerate) # Make sure it is a whole number
        game : GameController = self.game
        gameMap : GameMap = game.gameMap
        playerPosAsTile = player.GetPositionAsTile() # player position as tile coord
        screenSize = game.screen.get_size()

        if(qtyToGenerate != 0):
            # iterate through generation
            for generationIndex in range(0, qtyToGenerate):

                # get range of tiles not in players
                generationRanges = [] # each list in the list is a range (tuple) where objects can generate. If empty list they can't generate in this row
                totalRows = gameMap.rows # Get total possible rows as an int
                rowSize = gameMap.rowSize # How many tiles there r per row
                if(totalRows == 0):
                    gameMap.UpdateRows(screenSize[0], screenSize[1])
                if(totalRows == 0): # still zero despire being updated
                    return 
                for rowIndex in range(0,totalRows):
                    if(not (rowIndex == 1 or rowIndex == totalRows)):
                        rowRanges : list = [] # intialise the row ranges
                        generatedEnemyTiles : list = [] # list of enemy tiles as tuples
                        firstIntersectRecorded = False # bool of whether the first ineterse
                        # loop throuugh columns of row
                        lastColumnIntersect = 1 # initialised, the column of intersect 
                        for columnIndex in range(0, rowSize+1): # range exclusive
                            iteratedTile = (rowIndex, columnIndex)
                            nextTile = (rowIndex, columnIndex + 1) # next tile, it is handled if last column
                            interesctingColumn : int = columnIndex # init
                            
                            interesctingColumn = columnIndex
                            generatedATile : bool = False

                            if (iteratedTile == playerPosAsTile):
                                interesctingColumn = columnIndex
                                if(firstIntersectRecorded == False):
                                    firstIntersectRecorded = True
                                lastColumnIntersect = interesctingColumn
                            if(columnIndex == 1 or columnIndex == rowSize): #  last index
                                interesctingColumn = columnIndex
                                if(firstIntersectRecorded == False):
                                    firstIntersectRecorded = True
                                lastColumnIntersect = interesctingColumn # record the last intersect
                                if (lastColumnIntersect+1 != rowSize): # if last intersecting column + 1 is not the end 
                                    rowRanges.append((lastColumnIntersect+1,rowSize))
                                    generatedATile = True
                                    lastColumnIntersect = interesctingColumn # record as intersect so other math makes sense
                                # else, leave list empty
                            elif(((nextTile != iteratedTile) and (iteratedTile != playerPosAsTile)) or (not (iteratedTile in generatedEnemyTiles))): # check for intersection or iterated tile is not same as generated one
                                if(firstIntersectRecorded == True): # if first recorded intersect
                                    firstIntersectRecorded = False
                                    rowRanges.append((1, interesctingColumn-1)) # start at 1
                                    generatedATile = True
                                else: # not first
                                    rowRanges.append((lastColumnIntersect+1, interesctingColumn-1)) # from last intersect to current
                                    generatedATile = True
                            

                            if(generatedATile == True):
                                generatedEnemyTiles.append(iteratedTile)
                            
                        # Row doesn't intersect with snake
                        # print(rowDoesIntersectWithSnake)
                        

                        generationRanges.append(rowRanges) # add a list for each row

                    # end of row for loop
                
                # all of the chosen row indexes 
                chosenRowindexes = [] 

                #range is eclusive. Index is useless
                for index in range(0, qtyToGenerate):
                    #choose a random range
                    genRangesLength = len(generationRanges)
                    chosenRowIndex = random.randint(0, genRangesLength - 1)
                    chosenRowindexes.append(chosenRowIndex)

                # loop thru all rows
                for chosenRowIndex in chosenRowindexes: 
                    rowRangeList = generationRanges[chosenRowIndex]
                    rowRangeLength = len(rowRangeList) # length of list of elements in row range list. W
                    chosenRowRange : tuple = rowRangeList[random.randint(0,rowRangeLength - 1)] # a tuple of potential ranges
                    enemyTilePosition = (chosenRowIndex, random.randint(chosenRowRange[0],chosenRowRange[1])) # the chosen tile for fruit'
                    self.SpawnEnemy(enemyTilePosition) # add the fruit to map

                

                game = self.game
                currentLevel = game.level # get level
                self.lastLevelLoaded = currentLevel # finally set loaded objects
            self.enemiesLeft = qtyToGenerate # set enemies left

    def RenderEnemies(self):
        playerPosition : tuple = player.playerPosition # real player position
        playerSize = player.size
        enemySize = self.sizeXY
        enemyWidth = enemySize
        enemyHeight = enemySize
        enemyColour = self.enemyColour
 
        for enemyPositon in self.enemyPositions:
            # enemy position is in real coords
            tempPosRect = pygame.Rect(enemyPositon[0] - enemyWidth, enemyPositon[1] - enemyHeight, enemyWidth, enemyHeight)
            pygame.draw.rect(self.game.screen, enemyColour, tempPosRect)

            """
            enemyPoints = [] # a list of enemy points to render as polygon
            enemyPoints.append(enemyPositon) # bottom-left position
            enemyPoints.append((enemyPositon[0]+enemyWidth, enemyPositon[1])) # bottom-right
            enemyPoints.append((enemyPositon[0]+enemyWidth / 2, enemyPositon[1] - enemyHeight)) # top
            enemyMidPoint = (enemyPositon[0] + enemyWidth / 2, enemyPositon[1] - enemyHeight / 2)

            enemyPointAngle = 0 # default tp 0 for now
            playerMidPoint = (playerPosition[0] + playerSize[0]/2, playerPosition[1] - playerSize[1]/2) # midpoint, goal to point towards
            enemyTriTop = enemyPoints[2] # the top of enemy triangle
            playerTriTop = (playerPosition[0] + playerSize[0]/2, playerPosition[1] - playerSize[1])

            radiusOfEnemyTriangle = enemyHeight / 2 

            # check for intersect with imaginary circle around enemy and player midpoint, remember we want the enemy to point towards player, that is goal
            # There can't be a situation where there isn't an intersect

            # Search circle equation to find

            # Check if the sqrt part is positive. You can't square root negative numbers in the real plane (idk if u can in complex).
            # y will check for x intercept and x  for y. See my graph https://www.desmos.com/calculator/yjvgt7htmo

            # draw an imaginary line from player top to midpoint of enemy.
            # See my graph https://www.desmos.com/calculator/uh0fcsw30b
            # get the slope between the two points
            slope = 1 # default to 0
            if((enemyMidPoint[0] - playerMidPoint[0] != 0) and (enemyMidPoint[1] - playerMidPoint[1] != 0)):
                slope = (enemyMidPoint[1] - playerMidPoint[1]) / (enemyMidPoint[0] - playerMidPoint[0])
            yIntercept = playerMidPoint[1]-(slope*playerMidPoint[0])


            print("--------") 

            # I did math by hand but I still have ataxia so it's not the best, I'm also from Vicroia, Melbourne so I draw my p weird because that's the correct local spelling
            yBottomHalfPreSqrtResult = -1 * (pow(radiusOfEnemyTriangle, 2) - pow(enemyMidPoint[1], 2))
            yTopHalfPreSqrtResult = -1 * yBottomHalfPreSqrtResult
            
            if(yBottomHalfPreSqrtResult > 0):
                print(((math.sqrt(yBottomHalfPreSqrtResult))*slope)+yIntercept )
            if(yTopHalfPreSqrtResult > 0):
                print(((math.sqrt(yTopHalfPreSqrtResult))*slope)+yIntercept )

            finishedEquationY = None # init. Going to be a number, likely a float
            if(yBottomHalfPreSqrtResult >= 0 or yTopHalfPreSqrtResult >= 0): # positive or 0, there is an intersection
                posPreSqrtResult = None # init. Going to be a number, likely a float
                # get which one is positive
                if(yBottomHalfPreSqrtResult > 0 or abs(yBottomHalfPreSqrtResult) == 0):
                    posPreSqrtResult = yBottomHalfPreSqrtResult
                elif(yTopHalfPreSqrtResult > 0 or yTopHalfPreSqrtResult == 0):
                    posPreSqrtResult = yTopHalfPreSqrtResult
                
                finishedEquationY = ((math.sqrt(posPreSqrtResult))*slope)+yIntercept 
            else:
                print("neither y pre sqrt is above 0")
            
            # do the same for x
            xBottomHalfPreSqrtResult = -1 * (pow(radiusOfEnemyTriangle, 2) - pow(enemyMidPoint[0], 2))
            xTopHalfPreSqrtResult =  -1 * xBottomHalfPreSqrtResult
            xResult1 = 0
            xResult2 = 0

            print("-------")
            if(xBottomHalfPreSqrtResult > 0):
                print(((math.sqrt(xBottomHalfPreSqrtResult))-yIntercept)/slope )
            if(xTopHalfPreSqrtResult > 0):
                print(((math.sqrt(xTopHalfPreSqrtResult))-yIntercept)/slope)

            finishedEquationX = None # init. Going to be a number, likely a float
            if(xBottomHalfPreSqrtResult >= 0 or xTopHalfPreSqrtResult >= 0): # positive or 0, there is an intersection
                posPreSqrtResult = None # init. Going to be a number, likely a float
                # get which one is positive
                if(xBottomHalfPreSqrtResult > 0 or abs(xBottomHalfPreSqrtResult) == 0):
                    posPreSqrtResult = xBottomHalfPreSqrtResult
                elif(xTopHalfPreSqrtResult > 0 or xTopHalfPreSqrtResult == 0):
                    posPreSqrtResult = xTopHalfPreSqrtResult
                
                finishedEquationX = ((math.sqrt(posPreSqrtResult))-yIntercept)/slope 
            else:
                print("neither X pre sqrt is above 0")
                

            #print(yBottomHalfPreSqrtResult > 0)
            #print(yTopHalfPreSqrtResult > 0)
            
            if(math.isnan(finishedEquationX) == True):
                finishedEquationX = 0
                print("Got x as nan, defaulted to 0")
            if(math.isnan(finishedEquationY) == True):
                finishedEquationY = 0
                print("Got y as nan, defaulted to 0")
            finalPoint = numpy.add((finishedEquationX, finishedEquationY), (0,0))#(enemyTriTop))
            
            print(finalPoint)
            pygame.draw.circle(screen, "red", finalPoint, 3)
            print(playerPosition[1] > finishedEquationY)
            print(enemyPositon)
            """



    def Update(self):
        game : GameController = self.game
        lastLevelLoaded = self.lastLevelLoaded
        currentLevel = game.level
        maxEnemiesPerlevel = self.maxEnemiesPerlevel

        # If last level is not the same as curerent level
        if(lastLevelLoaded != currentLevel):
            # Determine how many enemies to generate
            qtyToGenerate = min(maxEnemiesPerlevel, currentLevel) # cap out at 10 enemies
             # Spawn enemies
            self.GenerateEnemies(qtyToGenerate)


# controls all fruit on map

tileSize = 20
gameMap = GameMap(tileSize)
game = GameController(gameMap, screen)

if (gameMap.errorOnCreation):
    print("!! There was an error creating the map !!")

inpCoords = (30,19) # input coordinates
print("input coords: (" + str(inpCoords[0]) + ", " + str(inpCoords[1]) +")")
tileCoords = GameMap.realToTileCoords(inpCoords, tileSize)
print(tileCoords)
realCoords = (GameMap.tileCoordsToReal(tileCoords, tileSize))
print(realCoords)
player = PlayerController(screen, game, tileSize)
enemyController = EnemyController(game, player)
#fruitController = FruitController(screen, gameMap, game)
gameControls = Controls.WASD

def handlePlayerMovement(moveDirection : int):
    print("Moving in Direction " + Direction.DirectionToString(moveDirection))
    player.ChangeDirection(moveDirection) # type checking is done in function

playerMovementKeysDown = {} # which keys are pressed down. Each key corresponds to index and vaalue is bool

"""
# Fills the movement keys dictionary with Falses
def fillMovementKeys():
    if(gameControls == Controls.WASD):
        # if pressed, is True
        if(pygame.K_w not in playerMovementKeysDown): # check if key exists
            playerMovementKeysDown[pygame.K_w] = False
        if(pygame.K_a not in playerMovementKeysDown):
            playerMovementKeysDown[pygame.K_a] = False
        if(pygame.K_s not in playerMovementKeysDown):
            playerMovementKeysDown[pygame.K_s] = False
        if(pygame.K_d not in playerMovementKeysDown):
            playerMovementKeysDown[pygame.K_d] = False
"""



# Handle key down, pass in the pressed key event as input. Is oj
def handleKeysDown() -> None:
    print("Called key down function") # Is only called once regardless of keys down
    
    
    keysPressed = pygame.key.get_pressed()

    moveDirection : Direction = None # initalise. Should be Direction enum

    AtLeastOneKeyPressed = False

    # if controls are wasd
    if(gameControls == Controls.WASD):

        # if pressed, is True
        if(pygame.K_w in playerMovementKeysDown): # check if key exists
            playerMovementKeysDown[pygame.K_w] = True # set value of key
        else:
            playerMovementKeysDown[pygame.K_w] = False
        if(pygame.K_a in playerMovementKeysDown):
            playerMovementKeysDown[pygame.K_a] = True # set value of key
        else:
            playerMovementKeysDown[pygame.K_a] = False
        if(pygame.K_s in playerMovementKeysDown):
            playerMovementKeysDown[pygame.K_s] = True # set value of key
        else:
            playerMovementKeysDown[pygame.K_s] = False
        if(pygame.K_d in playerMovementKeysDown):
            playerMovementKeysDown[pygame.K_d] = True # set value of key
        else:
            playerMovementKeysDown[pygame.K_d] = False
        
        wState = keysPressed[pygame.K_w]
        aState = keysPressed[pygame.K_a]
        sState = keysPressed[pygame.K_s]
        dState = keysPressed[pygame.K_d]

        # check if more than 1 are pressed
        totalPressed = 0

        if(wState == True):
            totalPressed += 1
            moveDirection = Direction.north
            # if not found or is found but not down
            keyFound = pygame.K_w in playerMovementKeysDown
            if(keyFound == False or (keyFound == True and playerMovementKeysDown[pygame.K_w] == False)):
                playerMovementKeysDown[pygame.K_w] = True
        if(aState == True):
            totalPressed += 1
            moveDirection = Direction.west
            keyFound = pygame.K_a in playerMovementKeysDown
            if(keyFound == False or (keyFound == True and playerMovementKeysDown[pygame.K_a] == False)):
                playerMovementKeysDown[pygame.K_a] = True
        if(sState == True):
            totalPressed += 1
            moveDirection = Direction.south
            keyFound = pygame.K_s in playerMovementKeysDown
            if(keyFound == False or (keyFound == True and playerMovementKeysDown[pygame.K_s] == False)):
                playerMovementKeysDown[pygame.K_s] = True
        if(dState == True):
            totalPressed += 1
            moveDirection = Direction.east
            keyFound = pygame.K_d in playerMovementKeysDown
            if(keyFound == False or (keyFound == True and playerMovementKeysDown[pygame.K_d] == False)):
                playerMovementKeysDown[pygame.K_d] = True

        if(totalPressed == 2):
            # check for north-west etc.
            if(wState == True and aState ==  True):
                moveDirection = Direction.northWest
                key = (pygame.K_w, pygame.K_a) # keys to achieve dierction
                keyFound = (key in playerMovementKeysDown) # check for existence of array
                if(keyFound == False or (keyFound == True and playerMovementKeysDown[key] == (False,False))):
                    playerMovementKeysDown[key] = (True, True)
            if(wState == True and dState ==  True):
                moveDirection = Direction.northEast
                key = (pygame.K_w, pygame.K_d) # keys to achieve dierction
                keyFound = (key in playerMovementKeysDown) # check for existence of array
                if(keyFound == False or (keyFound == True and playerMovementKeysDown[key] == (False,False))):
                    playerMovementKeysDown[key] = (True, True)
            if(sState == True and aState == True):
                moveDirection = Direction.southWest
                key = (pygame.K_s, pygame.K_a) # keys to achieve dierction
                keyFound = (key in playerMovementKeysDown) # check for existence of array
                if(keyFound == False or (keyFound == True and playerMovementKeysDown[key] == (False,False))):
                    playerMovementKeysDown[key] = (True, True)
            if(sState == True and dState == True):
                moveDirection = Direction.southEast
                key = (pygame.K_s, pygame.K_d) # keys to achieve dierction
                keyFound = (key in playerMovementKeysDown) # check for existence of array
                if(keyFound == False or (keyFound == True and playerMovementKeysDown[key] == (False,False) )):
                    playerMovementKeysDown[key] = (True, True)
        if (totalPressed > 0):
            AtLeastOneKeyPressed = True
        
    if(AtLeastOneKeyPressed == True and moveDirection != player.currentDirection):
        handlePlayerMovement(moveDirection)
        
def handleKeyUp(event: pygame.event.Event = None) -> None:
    playerMovementKeysEnum = gameControls
    keysUp = [] # what keys were pressed up, expressed as indexes
    if(playerMovementKeysEnum == Controls.WASD):
        # Check what key was unpressed
        keys = pygame.key.get_pressed() # get state of all keys
        
        #iterate through keys
        for keyDownIndex in playerMovementKeysDown.keys():
            keyDownValue = playerMovementKeysDown[keyDownIndex]
            #fillMovementKeys() # update the movement key states recorded
            # if key unpressed and (last state key exists and last state was down)
            if(type(keyDownIndex) != list and keys[pygame.K_w] == False and playerMovementKeysDown[pygame.K_w] == True):
                keysUp.append(pygame.K_w)
                playerMovementKeysDown[pygame.K_w] = False # ser new value of False
            if(type(keyDownIndex) != list and keys[pygame.K_a] == False and playerMovementKeysDown[pygame.K_a] == True):
                keysUp.append(pygame.K_a)
                playerMovementKeysDown[pygame.K_a] = False # ser new value of False
            if(type(keyDownIndex) != list and keys[pygame.K_s] == False and playerMovementKeysDown[pygame.K_s] == True):
                keysUp.append(pygame.K_s)
                playerMovementKeysDown[pygame.K_s] = False # ser new value of False
            if(type(keyDownIndex) != list and keys[pygame.K_d] == False and playerMovementKeysDown[pygame.K_d] == True):
                keysUp.append(pygame.K_d)
                playerMovementKeysDown[pygame.K_d] = False # ser new value of False
            if(type(keyDownIndex) == list and keys[keyDownIndex[0]] == False and keys[keyDownIndex[1] == False and playerMovementKeysDown[keyDownIndex[0]]] == True and playerMovementKeysDown[keyDownIndex[1]] == True): # if index is a list of combinations of number
                keysUp.append(keyDownIndex[0])
                keysUp.append(keyDownIndex[1])
                playerMovementKeysDown[keyDownIndex][0] = False # index by list and set
                playerMovementKeysDown[keyDownIndex][1] = False

    # qtyKeysUp = len(keysUp) # quantity 
    keysDown = [] # list of keys down
     
    for keyDownIndex in playerMovementKeysDown.keys():
        keyDownValue = playerMovementKeysDown[keyDownIndex]
        if((type(keyDownIndex) != list) and keyDownValue == True):
            keysDown.append(keyDownIndex) # append pygame index
        elif((type(keyDownIndex) == list) and keyDownValue[0] == True and keyDownValue[1] == True):
            keysDown.append(keyDownIndex) # append pygame indexes
    
    qtyKeysDown = len(keysDown) # quantity
    if(qtyKeysDown == 0): # stop moving
        handlePlayerMovement(Direction.none)
    if(qtyKeysDown > 0): # still might be moving
        handleKeysDown() # keep moving if still keys down
        

        
    

# Handle key up, pass in the pressed key event as input
while running:
    # fill screen with dark grey
    screen.fill((40,44,49))
    
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("Got quit event")
            running = False
        elif event.type == pygame.KEYDOWN: # handle key down
            handleKeysDown() # pass in key event and call func
        elif event.type == pygame.KEYUP: # handle key up
            handleKeyUp() # pass in key event

    if(game.end == False):
        player.Update() # update the player and move if enough time has passed. Func retunrs True if success
        enemyController.Update()
    # render snake below text in case player decides to go under text
    player.Render()
    enemyController.RenderEnemies()
    # player.RenderHitbox() # debugging
    if(game.end == False):
        pass
        #fruitController.updateFruits(playerSnake)
    #fruitController.renderFruits()
    if(game.end == False):
        player.RenderKillsText()
    else: # ended ==  True
        game.RenderEndGame() 


    # flip() the display to put your work on screen
    pygame.display.flip()
    
    clock.tick(150)  # limits FPS 

print("closing")
pygame.quit()
