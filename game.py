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

class Projectle():
    velocity = (0,0) # velocity is a vector2d (tuple) of how mmany pixels a projectile will travel in one second
    position = (0,0) # position of projectile, will change from velocity. This is centre of projectile
    radius : float = None # radius of projectile
    #startPosition = (0,0) # start position of projectile in real coords 
    shouldMoveProjectile = False # don't need to start
    launched : bool = False # whether projectile has started moving
    isEnemyProjectile : bool = False
    hitbox : pygame.Rect = None # Just a rect
    projectileEnemyColour = (223,224,99) # a yellow because yellow is easier for humans to notice
    projectileColour = (255,255,255) # default colour for non--enemy projectiles
    screen : pygame.surface.Surface = None # initalise
    owner : object = None # owner of projectile, could be player or enemy 
    hasCollided : bool = False # whether the projectile has collided with anything


    def __init__(self, owner, startPosition : tuple, velocity : tuple, screen : pygame.surface.Surface, isEnemyProjectile : bool = False, radius : float = 3 ) -> None:
        self.velocity = velocity
        self.screen = screen
        self.owner = owner
        #self.startPosition = startPosition
        self.position = startPosition # start position at start position. This is centre of projectile
        self.isEnemyProjectile = isEnemyProjectile
        self.radius = radius
        self.hitbox = pygame.Rect(startPosition[0]-radius, startPosition[1] - radius, radius* 2, radius * 2) # intialise

    
    # start moving the projectile 
    def StartProjectile(self):
        self.shouldMoveProjectile = True

    # time differemce is usually the amount of difference since the last update
    def MoveProjectile(self, timeDifference):
        velocity = self.velocity # use the velcotiy with time differennce to get amount moved
        moveAmnt = numpy.multiply(velocity, timeDifference/1000.0) # tuple of x and y move amount using velocity. /1000 to convert millis to seconds
        currentPosition = self.position 
        newPosition = tuple(currentPosition + moveAmnt) 
        radius = self.radius
        self.position = newPosition
        self.launched = True
        self.hitbox = pygame.Rect(newPosition[0] - radius, newPosition[1] - radius, radius*2, radius *2)
        #print("here")
    
    def Render(self):
        projectilePos = self.position
        projectileRadius = self.radius

        # Draw projectile
        if(self.isEnemyProjectile == True):
            pygame.draw.circle(self.screen, self.projectileEnemyColour, projectilePos, projectileRadius)
        else: # not an enemy projectile
            pygame.draw.circle(self.screen, self.projectileColour, projectilePos, projectileRadius)

    def RenderHitbox(self):
        hitboxRect = self.hitbox
        pygame.draw.rect(self.screen, "white", hitboxRect)

class ProjectileHandler():
    projectiles : list = [] # list of Proectile objects
    projectilesLength = 0
    game : GameController = None # initalise
    lastUpdate = getCurrentMillisecondTime() # last update in millis
    startingLevel = 1 
    removingAProjectile : bool = False

    def __init__(self, game : GameController) -> None:
        self.game = game

    # pass in projectile object
    def RemoveProjectile(self, projectile : Projectle):
        projectileIndex = self.projectiles.index(projectile)
        self.removingAProjectile = True
        self.projectiles.pop(projectileIndex)
       #print("Removed a projectile")
    
    # updates all projectiles
    def UpdateProjectiles(self, player, enemies):
        currentTime = getCurrentMillisecondTime()
        timeDifference = currentTime - self.lastUpdate # difference in time in millis
        #enemyProjectiles : list = []

        
        for projectileIndex in range(0, len(self.projectiles)):
            # prevent an error
            if(self.removingAProjectile == True):
                self.removingAProjectile = False # set to false again
                return
            projectile : Projectle = self.projectiles[projectileIndex]

            if(projectile.shouldMoveProjectile == True):
                projectile.MoveProjectile(timeDifference)
            #if(projectile.isEnemyProjectile == True):
                #enemyProjectiles.append(projectile)
            # Detect a hit
                
            
            if(projectile.hasCollided == False):
                # is enemy, check hit with player
                if(projectile.isEnemyProjectile == True):
                    if(projectile.hitbox.colliderect(player.hitbox) == True):
                        projectile.hasCollided = True
                        enemy : Enemy = projectile.owner
                        enemy.lastProjectileCleanupTime = getCurrentMillisecondTime()
                        self.RemoveProjectile(projectile) # remove from list
                        enemy.projectile = None
                        player.hp -= enemy.damage

                        print("Player hit by enemy")
                # else, check for a hit with any enemy hitboxes
                else:
                    for enemy in enemies:
                        if(projectile.hitbox.colliderect(enemy.hitbox)):
                            projectile.hasCollided = True
                            self.RemoveProjectile(projectile) # remove from list
                            enemy.hp -= player.damage
                            print("Enemy hit by player")

        #lengthOfEnemyProjectiles = len(enemyProjectiles)
        #if(lengthOfEnemyProjectiles == 0 and self.game.level > self.startingLevel):
            #self.game.level += 1 # Increment level
        
        

        self.lastUpdate = currentTime #setup next update

    # Add projectile to managed projectiles
    def AddProjectile(self, projectile):
        self.projectiles.append(projectile)

    def RenderProjectiles(self , shouldRenderHiibox : bool = False):
        for projectile in self.projectiles:
            projectile.Render()
            if(shouldRenderHiibox == True):
                projectile.RenderHitbox()




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
    hp = 100 # health
    directionBeforeRest : int = None # intended to be set before direction.none is made current direction
    projectileCooldown : int = 500 # how may millis until player can fire
    timeSinceLastShoot : int = 0 # in millis
    damage : int = 50 # damage to enemies
    projectileSpeed : int = 300 # in pixel/second
    projectiles : list = [] # list of player projcetile objects

    # constrcutor must have screen and GameMap and tilesiaze arg
    def __init__(self, screen : pygame.surface, game : GameController, tileSize : int ) -> None:
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

    # get angle based on direction of player. IN DEGREES
    def GetPlayerAngleBasedOnDirection(self, direction : Direction) -> int:
        playerDirectionAngle = 0 # default or pointing North. In degrees cos they're easier to read

        if(direction == Direction.east):
            playerDirectionAngle = 90
        elif(direction == Direction.south):
            playerDirectionAngle = 180
        elif(direction == Direction.west):
            playerDirectionAngle = 270
        elif(direction == Direction.northEast):
            playerDirectionAngle = 45
        elif(direction == Direction.northWest):
            playerDirectionAngle = 315 # 270 + 45
        elif(direction == Direction.southEast):
            playerDirectionAngle = 135 # 180 - 45
        elif(direction == Direction.southWest):
            playerDirectionAngle = 225 # 180 + 45

        return playerDirectionAngle

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

        playerDirectionAngle = self.GetPlayerAngleBasedOnDirection(playerDirection) # In degrees cos they're easier to read. Angles are counter-clockwise
        
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
    
    # Gets the real coord of point of player that is tip
    def GetTipOfPlayer(self) -> tuple:
        playerPosition = self.playerPosition # position of player
        playerDirection = self.currentDirection
        if(playerDirection == Direction.none and self.directionBeforeRest != None):
            playerDirection = self.directionBeforeRest # set it to direction before stop

        playerWidth = self.size[0]
        playerHeight = self.size[1]
        

        playerTip = ((playerPosition[0] + playerWidth/2,playerPosition[1]-playerHeight)) # create tip
        midPoint = (playerPosition[0] + playerWidth / 2, playerPosition[1] - playerHeight / 2) # centre of triangle

        playerAngle = math.radians(self.GetPlayerAngleBasedOnDirection(playerDirection) )
        return rotate2DVectorAroundPoint(playerTip, midPoint, playerAngle) # the tip rotated

    # Shoot a projectile in player direction
    def Shoot(self):
        currentTime = getCurrentMillisecondTime()
        if(currentTime - self.timeSinceLastShoot < self.projectileCooldown):
            print("Not shooting, not enough time has passed. \nTime difference:"+str(currentTime- self.timeSinceLastShoot)+"\nCooldown:"+ str(self.projectileCooldown))
            return
        print("shooting")
        tipOfPlayer = self.GetTipOfPlayer()
        playerDirection = self.currentDirection
        if(playerDirection == Direction.none and self.directionBeforeRest != None):
            playerDirection = self.directionBeforeRest # set it to direction before stop
        # shoot from this angle
        #print("----")
        #print("Shooting in direction: "+Direction.DirectionToString(playerDirection))
        #print(self.GetPlayerAngleBasedOnDirection(playerDirection))
        angleOfCurrentDirection = math.radians(self.GetPlayerAngleBasedOnDirection(playerDirection) - 90)
        # See desmos graph https://www.desmos.com/calculator/z3fngmdr6p
        normalisedVelocity = (math.cos(angleOfCurrentDirection), math.sin(angleOfCurrentDirection))
        velocity = numpy.multiply(normalisedVelocity, self.projectileSpeed)

        projectle = Projectle(self, tipOfPlayer, velocity, screen)
        projectileHandler.AddProjectile(projectle) # add to handler
        projectle.StartProjectile() # start moving
        self.timeSinceLastShoot = currentTime # setup next shot

        
    lastDirectionChangeTime = 0 # in millis
    # changes snake Direction
    def ChangeDirection(self, moveDirection : int) -> None:
        # type check
        if(type(moveDirection) != int):
            raise Exception("ERROR: Didn't pass in an int")
        
        # save the old direction
        oldDirection = self.currentDirection
        #print("Old direction: "+Direction.DirectionToString(oldDirection))
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
        # check player hp
        hp = player.hp
        if(hp <= 0):
            print("hp is:"+str(hp)+"\nEnding the game")
            self.game.EndGame("Hp is less than or equal to 0")

        # Check if enough time has passed
        currentTimeInMilliseconds = getCurrentMillisecondTime()
        timeDifferenceInMillis = currentTimeInMilliseconds - self.lastMoveTime # time diifference netween current and last move in milliseconds
        if((timeDifferenceInMillis <= movePlayerDelay) or (self.lastMoveTime > 0 and timeDifferenceInMillis <= movePlayerDelay)):
            # print("WARN: not enough time has passed between player movements, skipping. Time difference is " + str(timeDifferenceInMillis)+" and delay is "+ str(moveSnakeDelay))
            return
        # now assign last move time to new move time
        self.lastMoveTime = currentTimeInMilliseconds

        # the Direction the player is facing
        
        # Move the player
        self.MoveInCurrentDirection()

        return True


enemyId = 0 # start at 0

class Enemy():
    id : int = None # set in init
    position : tuple = (0,0) # real coords of enemy position
    projectileReady : bool = False
    projectile : Projectle  = None # a projectile that is under the enemy control
    projectileCooldown : int = 1000 # After this many millis have passed, spawn a new projectile
    lastProjectileCleanupTime = 0 # last time in millis since the enemy's projectilem was erased
    colour = (252, 29, 54) # colour of enemy
    hitbox : pygame.Rect = None
    sizeXY = None
    screen : pygame.surface.Surface = None
    hp = 50 # survive one hit
    damage = 20 # how much damage enemy does to player

    player = None # init in constructor
    sizeOfEnemyXY : int = None

    def __init__(self, screen : pygame.surface.Surface, player : PlayerController, sizeOfEnemyXY : int, initialPosition : tuple, sizeXY) -> None:
        global enemyId
        enemyId += + 1
        self.player = player
        self.sizeOfEnemyXY = sizeOfEnemyXY
        self.position = initialPosition
        self.screen = screen
        self.sizeXY = sizeXY
        self.hitbox = pygame.Rect(initialPosition[0], initialPosition[1] - sizeXY, sizeXY, sizeXY)

    # create a projectile. Pass in speed as arg, single val
    def createProjectile(self, speed : float, projectileHandler : ProjectileHandler):
        player = self.player
        sizeOfEnemyXY = self.sizeOfEnemyXY
        enemyPositon = self.position
        playerPosition = player.playerPosition    
        playerSize = player.size
        playerMidPoint = (playerPosition[0] + playerSize[0]/2, playerPosition[1] - playerSize[1]/2)
        enemyMidPoint = (enemyPositon[0] + sizeOfEnemyXY/2, enemyPositon[1] - sizeOfEnemyXY/2)

        difOfEnemyToPlayer = numpy.subtract(playerMidPoint,enemyMidPoint) # vector is relative to 0
        magOfEnemyToPlayer = math.sqrt(pow(difOfEnemyToPlayer[0],2) + pow(difOfEnemyToPlayer[1],2) )
        # Normalise
        originVecNormalised = numpy.divide(difOfEnemyToPlayer, magOfEnemyToPlayer) # divide each point by distance. vector is relative to 0
        velocityVec = numpy.multiply(originVecNormalised, speed) # Multiple normalised vector by speed to get velocity. Each axis neeeds to be mmultiplied by number

        # add projectile
        projectile = Projectle(self, enemyMidPoint, velocityVec, screen, True)
        projectile.StartProjectile() # start it moving
        projectileHandler.AddProjectile(projectile) # Add to managed projectiles
        self.projectile = projectile
    
    def Render(self):
        # enemy position is in real coords
        position = self.position
        sizeXY = self.sizeXY
        enemyWidth = sizeXY
        enemyHeight = sizeXY
        enemyColour = self.colour

        # Draw at top-left
        tempPosRect = pygame.Rect(position[0], position[1] - enemyHeight, enemyWidth, enemyHeight)
        pygame.draw.rect(self.screen, enemyColour, tempPosRect)

    def RenderHitbox(self):
        hitboxRect = self.hitbox
        pygame.draw.rect(self.screen, "white", hitboxRect )

    def GetANewProectileIsReady(self, currentTime) -> bool:
        lastProjectileCleanupTime = self.lastProjectileCleanupTime# last time in millis since the enemy's projectilem was erased
        projectileCooldown = self.projectileCooldown
        if(lastProjectileCleanupTime == 0):
            self.lastProjectileCleanupTime = currentTime # init as current time
        # time difference is more than cooldown and not launched in projectile or never created a projectile
        #print("--------")
        #print(currentTime - lastProjectileCleanupTime)
        #print(projectileCooldown)
        if((currentTime - lastProjectileCleanupTime) >= projectileCooldown and ((self.projectile != None and self.projectile.launched == False) or self.projectile == None) ):
            return True
        else:
            return False
     
# Spawn enemies and control them
class EnemyController():
    lastLevelLoaded = 0 # the last level with enemies that is loaded. Start at 0 because 1 requires loading
    game : GameController = None
    maxEnemiesPerlevel = 8
    enemies = [] # a list of enemies
    player : PlayerController = None
    enemySizeXY : int = 20 # size of a single enemy
    enemiesLeft = 1 # start
    projectileHandler = None 
    enemyProjectileSpeed = 240 # speed in pixels/second

    def __init__(self, game : GameController, player : PlayerController, projectileHandler : ProjectileHandler ) -> None:
        self.game = game
        self.player = player
        self.projectileHandler = projectileHandler
        game.enemyController = self # set enemy controller

    # Spawmn a singular enemy, pass in a real position
    def SpawnEnemy(self, enemyPosition):
        newEnemy = Enemy(self.game.screen, self.player, self.enemySizeXY, enemyPosition, self.enemySizeXY)
        self.enemies.append(newEnemy)
    

    def RemoveEnemy(self, enemy : Enemy):
        enemyIndex = self.enemies.index(enemy)
        self.enemies.pop(enemyIndex) # delete from list
        del enemy # kill enemy


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
    
    def GetEnemyPositions(self) -> list:
        endList = []
        for enemy in self.enemies:
            #enemy : Enemy = enemy
            enemyPos = enemy.position
            endList.append(enemyPos)
        return endList

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
                # start and end need to be minused by 1 cos iterated range is zero based
                startRow = 2 # the row and column to start from
                startColumn = 2
                endRow = totalRows - 1 # the row and column to end on
                endColumn = endRow # same same, the width and height should be equal or square
                game : GameController = self.game
                gameMap : GameMap = game.gameMap
                tileSize = gameMap.tileSize
                if(totalRows == 0):
                    gameMap.UpdateRows(screenSize[0], screenSize[1])
                if(totalRows == 0): # still zero despite being updated
                    return 
                for rowIndex in range(0,totalRows):
                    if(not (rowIndex < (startRow-1) or rowIndex > (endRow-1))):
                        rowRanges : list = [] # intialise the row ranges
                        generatedEnemyTiles : list = [] # list of enemy tiles as tuples
                        
                        # loop throuugh columns of row
                        lastColumnIntersect = startColumn # initialised, the column of intersect. Start at start
                        tileDidIntersect : bool = False
                        for columnIndex in range(0, rowSize): # range exclusive
                            iteratedTile = (rowIndex+1, columnIndex+1)
                            #nextTile = (rowIndex, iteratedTile[1] + 1) # next tile, it is handled if last column
                            interesctingColumn : int = None # init
                            firstIntersectRecorded = False # bool of whether the first inetersect
                            dontAddToRowRanges : bool = False # only set to false if added to row ranges already 

                            # if column isn't less than start or greater than end index
                            if(not (columnIndex < (startColumn-1) or columnIndex > (endColumn-1))):
                                # Check for intersect and not last or first column
                                if (iteratedTile == playerPosAsTile or (iteratedTile in generatedEnemyTiles) and columnIndex != (endColumn-1) and columnIndex != (startColumn-1)):
                                    interesctingColumn = columnIndex
                                    if(firstIntersectRecorded == False):
                                        firstIntersectRecorded = True
                                    lastColumnIntersect = interesctingColumn
                                    tileDidIntersect = True
                                        # lastColumnIntersect = interesctingColumn # record as intersect so other math makes sense
                                elif(columnIndex == (endColumn-1)): # last column index for row 
                                    # no intersect with lastColumnIntersect+1 and it is not same as end column
                                    #print("here")
                                    if(not ((lastColumnIntersect+1) == playerPosAsTile or ((lastColumnIntersect+1) in generatedEnemyTiles)) or (lastColumnIntersect+1 == endColumn)):
                                        if(lastColumnIntersect == startColumn):
                                            rowRanges.append((startColumn,endColumn))
                                        else:
                                            rowRanges.append((lastColumnIntersect+1,endColumn))
                                    dontAddToRowRanges = True # skip
                                elif(columnIndex == (startColumn-1)): # else is, start column, skip
                                    dontAddToRowRanges = True # skip
                                else: # else, no intersect
                                    dontAddToRowRanges = True

                                # handle intersects
                                if(dontAddToRowRanges == False):
                                    #print("here")
                                    if(firstIntersectRecorded == True): # if first recorded intersect
                                        firstIntersectRecorded = False
                                        rowRanges.append((startColumn, interesctingColumn-1)) # start at start column
                                    else: # not first
                                        rowRanges.append((lastColumnIntersect+1, interesctingColumn-1)) # from last intersect to current
                                    
                                

                                if(tileDidIntersect == True):
                                    generatedEnemyTiles.append(iteratedTile)
                                
                            else:
                                continue # start or end column, skip (cotinue onto next iteration)
                            
                        #if(tileDidIntersect == False): # tile didn't intersect
                              # start to end. # - 1 cos zero based
                              #rowRanges.append((startColumn,endColumn))

                        # Row doesn't intersect with snake
                        # print(rowDoesIntersectWithSnake)
                        

                        generationRanges.append(rowRanges) # add a list for each row
                    else:
                        generationRanges.append(None) # add a none element
                    # end of row for loop
                
                # all of the chosen row indexes 
                chosenRowindexes = [] 

                #range is eclusive. Index is useless
                for index in range(0, qtyToGenerate):
                    #choose a random range
                    genRangesLength = len(generationRanges)
                    chosenRowIndex = random.randint(startRow-1, endRow - 1)
                    chosenRowindexes.append(chosenRowIndex)

                # loop thru all rows
                for chosenRowIndex in chosenRowindexes: 
                    rowRangeList = generationRanges[chosenRowIndex]
                    rowRangeLength = len(rowRangeList) # length of list of elements in row range list. W
                    chosenRowRange : tuple = rowRangeList[random.randint(0, rowRangeLength-1)] # a tuple of potential ranges
                    enemyRealPosition = GameMap.tileCoordsToReal((chosenRowIndex, random.randint(chosenRowRange[0],chosenRowRange[1])), tileSize) # the tile to real coords'
                    self.SpawnEnemy(enemyRealPosition) # add the fruit to map

                

                game = self.game
                currentLevel = game.level # get level
                self.lastLevelLoaded = currentLevel # finally set loaded objects
            self.enemiesLeft = qtyToGenerate # set enemies left

    def RenderEnemies(self, renderHitboxes : bool = False):
        for enemy in self.enemies:
            enemy.Render()
            if(renderHitboxes == True):
                enemy.RenderHitbox()

    def Update(self):
        game : GameController = self.game
        lastLevelLoaded = self.lastLevelLoaded
        currentLevel = game.level
        maxEnemiesPerlevel = self.maxEnemiesPerlevel
        enemiesDead : list = [] # list of enemies to kill


        # loop through all enemies
        enemies : list = self.enemies
        for enemy in enemies:
            enemy : Enemy = enemy # for writing code, includes hint
            if(enemy.hp <= 0): # enemy died
                enemiesDead.append(enemy)
                continue # skip this enemy

            currentTime = getCurrentMillisecondTime()
            #enemyProjectileWidth =  enemy.sizeOfEnemyXY
            #enemyProjectileHeight =  enemy.sizeOfEnemyXY
            enemyProjectile : Projectle = enemy.projectile
            enemyProjectilePosition = None # inir
            currentTime = getCurrentMillisecondTime()
            if (enemyProjectile != None):
                enemyProjectilePosition = enemyProjectile.position
            #print(enemy.GetANewProectileIsReady(currentTime))
            if(enemy.GetANewProectileIsReady(currentTime) == True):    
                enemy.createProjectile(self.enemyProjectileSpeed, self.projectileHandler) # Create a eew projectile
            
            # enemy projectile exists and is Out of bounds
            if((enemyProjectile != None) and (enemyProjectilePosition[0] < 0 or enemyProjectilePosition[0] > screenSize or enemyProjectilePosition[1] < 0 or enemyProjectilePosition[1] > screenSize)):
                projectileHandler.RemoveProjectile(enemyProjectile)
                enemy.projectile = None
                enemy.lastProjectileCleanupTime = currentTime # set last cleanup time
        
        for enemy in enemiesDead:
            self.RemoveEnemy(enemy)
        

        

        print("---")
        print(len(self.enemies))
        # If last level is not the same as curerent level
        if(lastLevelLoaded != currentLevel):
            
            # Determine how many enemies to generate
            qtyToGenerate = min(maxEnemiesPerlevel, currentLevel) # cap out at 10 enemies
             # Spawn enemies
            self.GenerateEnemies(qtyToGenerate)
            self.lastLevelLoaded = currentLevel
        
        print(len(self.enemies))
        enemiesLength = len(self.enemies)
        print(len(self.enemies))
        # no more enemies
        if(enemiesLength == 0):
            self.game.level += 1 # go to next level
            print("Going to next level:"+str(self.game.level))

# controls all fruit on map

tileSize = 20
gameMap = GameMap(tileSize)
game = GameController(gameMap, screen)
projectileHandler = ProjectileHandler(game) 

if (gameMap.errorOnCreation):
    print("!! There was an error creating the map !!")

inpCoords = (30,19) # input coordinates
print("input coords: (" + str(inpCoords[0]) + ", " + str(inpCoords[1]) +")")
tileCoords = GameMap.realToTileCoords(inpCoords, tileSize)
print(tileCoords)
realCoords = (GameMap.tileCoordsToReal(tileCoords, tileSize))
print(realCoords)
player = PlayerController(screen, game, tileSize)
enemyController = EnemyController(game, player, projectileHandler)
#fruitController = FruitController(screen, gameMap, game)
gameControls = Controls.WASD

def handlePlayerMovement(moveDirection : int):
    #print("Moving in Direction " + Direction.DirectionToString(moveDirection))
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
    #print("Called key down function") # Is only called once regardless of keys down
    
    keysPressed = pygame.key.get_pressed()

    moveDirection : Direction = None # initalise. Should be Direction enum

    AtLeastOneKeyPressed = False

    # Shoot button is spacebar
    if(keysPressed[pygame.K_SPACE] == True ):
        #print(player.currentDirection)
        player.Shoot()
    
    
    
    # if controls are wasd
    if(gameControls == Controls.WASD):
        # if pressed, is True

        wState = keysPressed[pygame.K_w]
        aState = keysPressed[pygame.K_a]
        sState = keysPressed[pygame.K_s]
        dState = keysPressed[pygame.K_d]
        if(pygame.K_w in playerMovementKeysDown and wState == True): # check if key exists
            playerMovementKeysDown[pygame.K_w] = True # set value of key
        else:
            playerMovementKeysDown[pygame.K_w] = False # default to up
        if(pygame.K_a in playerMovementKeysDown and aState == True):
            playerMovementKeysDown[pygame.K_a] = True # set value of key
        else:
            playerMovementKeysDown[pygame.K_a] = False # default to up
        if(pygame.K_s in playerMovementKeysDown and sState == True):
            playerMovementKeysDown[pygame.K_s] = True # set value of key
        else:
            playerMovementKeysDown[pygame.K_s] = False # default to up
        if(pygame.K_d in playerMovementKeysDown and dState == True):
            playerMovementKeysDown[pygame.K_d] = True # set value of key
        else:
            playerMovementKeysDown[pygame.K_d] = False # default to up
        
        

        if(wState == False and aState == False and sState == False and dState == False):
            return # not w, a, s or d

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
    #print(player.currentDirection)
        
def handleKeyUp(event: pygame.event.Event = None) -> None:
    playerMovementKeysEnum = gameControls
    keysUp = [] # what keys were pressed up, expressed as indexes
    # If controls == WASD 
    keysDownBefore = [] # list of keys that were down
    movementKeys = [] # list of all movement keys as int enum
    
    
    if(playerMovementKeysEnum == Controls.WASD):
        # Check what key was unpressed
        keys = pygame.key.get_pressed() # get state of all keys
        
        movementKeys = [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]
        """"
        print("---------")
        print(pygame.K_SPACE)
        print(keys[pygame.K_SPACE])
        print(movementKeys)
        """
        for keyIndex in playerMovementKeysDown.keys():
            keyValue = playerMovementKeysDown[keyIndex]
            if((type(keyIndex) != list) and keyValue == True and keyIndex in movementKeys):
                
                keysDownBefore.append(keyIndex) # append pygame index
                playerMovementKeysDown[keyIndex] = False # now set to up
                
            elif((type(keyIndex) == list) and keyIndex[0] == True and keyIndex[1] == True and keyValue[0] in movementKeys and keyValue[1] in movementKeys):
                keysDownBefore.append(keyIndex[0]) # append pygame indexes
                keysDownBefore.append(keyIndex[1]) # append pygame indexes
                playerMovementKeysDown[keyIndex][0] = False # index by list and set. Now set to up
                playerMovementKeysDown[keyIndex][1] = False # now set to up

        #iterate through keys
        for keyIndex in playerMovementKeysDown.keys():
            keyValue = playerMovementKeysDown[keyIndex]
            #fillMovementKeys() # update the movement key states recorded
            # if key unpressed and (last state key exists and last state was down)
            if(type(keyIndex) != list and keyIndex in playerMovementKeysDown and pygame.K_w in keysDownBefore):
                keysUp.append(keyIndex)
            if(type(keyIndex) == list and (keyIndex[0] in playerMovementKeysDown or keyIndex[1] in playerMovementKeysDown) and keys[keyIndex[0]] == False and keys[keyIndex[1]] == False and playerMovementKeysDown[keyIndex[0]] == True and playerMovementKeysDown[keyIndex[1]] == True): # if index is a list of combinations of number
                keysUp.append(keyIndex[0])
                keysUp.append(keyIndex[1])


    # qtyKeysUp = len(keysUp) # quantity 
    
    
    
    allKeys = pygame.key.get_pressed()
    
    movementKeysDownCurrently = []

    keyIndex = 0
    for keyIndex in movementKeys:
        # If key index is in keys up and it is currently down
        #print(keyDownIndex)
        keyValue = allKeys[keyIndex]
        if(keyValue == True):
            movementKeysDownCurrently.append(keyIndex)
        keyIndex += 1

    
    AMovementKeyWasDownBefore : bool = False
    
    
    if(len(keysDownBefore) > 0):
        AMovementKeyWasDownBefore = True
    """
    # WASD keys r up
    if(gameControls == Controls.WASD and AKeyWasDownBefore == False and not(pygame.K_w in keysUp and pygame.K_a in keysUp and pygame.K_s in keysUp and pygame.K_d in keysUp)):
        return
    """



    if(gameControls == Controls.WASD and AMovementKeyWasDownBefore == False and len(movementKeysDownCurrently) == 0):
        return # end here
    """
    print(gameControls == Controls.WASD and AKeyWasDownBefore == False and allKeys[pygame.K_w] == False and allKeys[pygame.K_w] == False and allKeys[pygame.K_w] == False and allKeys[pygame.K_w] == False)
    if(gameControls == Controls.WASD and AKeyWasDownBefore == False and allKeys[pygame.K_w] == False and allKeys[pygame.K_w] == False and allKeys[pygame.K_w] == False and allKeys[pygame.K_w] == False):
        return
    """

    qtyKeysDown = len(movementKeysDownCurrently) # quantity
    if(qtyKeysDown == 0 ): # stop moving
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
        projectileHandler.UpdateProjectiles(player, enemyController.enemies)
    # render snake below text in case player decides to go under text
    player.Render()
    projectileHandler.RenderProjectiles()
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
