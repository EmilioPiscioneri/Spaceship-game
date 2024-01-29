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
    level = 1 # what level the game is on 
    end = False # end the game bool
    endReason : str = "" # Reason for ending
    gameEndedTextFontSize = 64
    

    # Ends a game
    def EndGame(self, reason : str):
        self.end = True # Stops certaining things from updating and rendering
        self.endReason = reason

    # Renders the end game text and reason
    def RenderEndGame(self, screen : pygame.surface.Surface) -> None:
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
    gameMap = None # initialise
    killsTextPadding = (10,10) # Padding pixels from top-left to give tjhe length text
    killsTextFontSize = 32 # font size of the length text
    playerSpeed : int = 10 # how many pixels the player moves per frame
    colour = (255,255,255) # The colour of the player
    kills = 0 # how many total kills the player has
    hitbox : pygame.rect = None # just a rect, does not hold the render. Updated on .Render()
    hitboxColour = (151, 236, 239) # For debugging
    #hitboxOutlineSize = 3 # For debugging, width of outline in pixels

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
        width = self.size[0]
        height = self.size[1]
        hitbox = pygame.Rect(startLocation[0], startLocation[1] - height, width, height) # do - height because canvas is top left based
        self.hitbox = hitbox
        # -- More init
        self.tileSize = tileSize
        self.screen = screen
        self.game = game

    # move the player in self.currentDirection 
    def MoveInCurrentDirection(self) -> None:
        currentDirection = self.currentDirection
        lastPlayerPosition : tuple = self.playerPosition
        playerSpeed : int = self.playerSpeed # how many pixels per movement
        newPlayerPos : tuple = lastPlayerPosition

        if(currentDirection == Direction.north): # moved up
            newPlayerPos = (lastPlayerPosition[0], lastPlayerPosition[1] - playerSpeed)
        elif(currentDirection == Direction.south): # moved down
            newPlayerPos = (lastPlayerPosition[0], lastPlayerPosition[1] + playerSpeed)
        elif(currentDirection == Direction.east): # moved right
            newPlayerPos = (lastPlayerPosition[0] + playerSpeed, lastPlayerPosition[1])
        elif(currentDirection == Direction.west): # moved left
            newPlayerPos = (lastPlayerPosition[0] - playerSpeed, lastPlayerPosition[1])
            #Diagonal direction. Divide by 2 from the addittion of movement on each axis to avoid 2 x speed movement

        elif(currentDirection == Direction.northWest): # moved up-left
            newPlayerPos = numpy.add(lastPlayerPosition, numpy.divide((-1 * playerSpeed,-1 * playerSpeed), 2))
        elif(currentDirection == Direction.northEast): # moved up-right
            newPlayerPos = numpy.add(lastPlayerPosition, numpy.divide((playerSpeed,-1 * playerSpeed), 2))
        elif(currentDirection == Direction.southEast): # moved down right
            newPlayerPos = numpy.add(lastPlayerPosition, numpy.divide((playerSpeed,playerSpeed), 2))
        elif(currentDirection == Direction.southWest): # moved down left
            newPlayerPos = numpy.add(lastPlayerPosition, numpy.divide((-1*playerSpeed,playerSpeed), 2))
        
        self.playerPosition = newPlayerPos # set new pos 

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
        
        playerWidth = self.size[0]
        playerHeight = self.size[1]
        

        playerPoints = [] # list of real coords
        playerPoints.append((playerPosition)) # start at bottom-left
        playerPoints.append((playerPosition[0] + playerWidth, playerPosition[1])) # create bottom-right
        playerPoints.append((playerPosition[0] + playerWidth/2,playerPosition[1]-playerHeight)) # create top
        midPoint = (playerPosition[0] + playerWidth / 2, playerPosition[1] - playerHeight / 2) # centre of triangle

        playerDirectionAngle = 0 # default or pointing North. In degrees cos they're easier to read

        # No Need to do north. Keep in mind the angle is is counter-clockwise
        if(self.currentDirection == Direction.east):
            playerDirectionAngle = 90
        elif(self.currentDirection == Direction.south):
            playerDirectionAngle = 180
        elif(self.currentDirection == Direction.west):
            playerDirectionAngle = 270
        elif(self.currentDirection == Direction.northEast):
            playerDirectionAngle = 45
        elif(self.currentDirection == Direction.northWest):
            playerDirectionAngle = 315 # 270 + 45
        elif(self.currentDirection == Direction.southEast):
            playerDirectionAngle = 135 # 180 - 45
        elif(self.currentDirection == Direction.southWest):
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

        
        
        # move snake
        # print(Direction.DirectionToString(Direction.getOppositeDirection(self.currentDirection)))
        # print(Direction.DirectionToString(moveDirection))
        self.currentDirection = moveDirection
            
    
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
    


# controls all fruit on map

tileSize = 20
gameMap = GameMap(tileSize)
game = GameController()

if (gameMap.errorOnCreation):
    print("!! There was an error creating the map !!")

inpCoords = (30,19) # input coordinates
print("input coords: (" + str(inpCoords[0]) + ", " + str(inpCoords[1]) +")")
tileCoords = GameMap.realToTileCoords(inpCoords, tileSize)
print(tileCoords)
realCoords = (GameMap.tileCoordsToReal(tileCoords, tileSize))
print(realCoords)
player = PlayerController(screen, gameMap, tileSize)
#fruitController = FruitController(screen, gameMap, game)
gameControls = Controls.WASD

def handlePlayerMovement(moveDirection : int):
    print("Moving in Direction " + Direction.DirectionToString(moveDirection))
    player.currentDirection = moveDirection
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
            if(wState == True and dState ==  True):
                moveDirection = Direction.northEast
            if(sState == True and aState == True):
                moveDirection = Direction.southWest
            if(sState == True and dState == True):
                moveDirection = Direction.southEast
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
        
        #fillMovementKeys() # update the movement key states recorded
        # if key unpressed and (last state key exists and last state was down)
        if(keys[pygame.K_w] == False and playerMovementKeysDown[pygame.K_w] == True):
            keysUp.append(pygame.K_w)
            playerMovementKeysDown[pygame.K_w] = False # ser new value of False
        if(keys[pygame.K_a] == False and playerMovementKeysDown[pygame.K_a] == True):
            keysUp.append(pygame.K_a)
            playerMovementKeysDown[pygame.K_a] = False # ser new value of False
        if(keys[pygame.K_s] == False and playerMovementKeysDown[pygame.K_s] == True):
            keysUp.append(pygame.K_s)
            playerMovementKeysDown[pygame.K_s] = False # ser new value of False
        if(keys[pygame.K_d] == False and playerMovementKeysDown[pygame.K_d] == True):
            keysUp.append(pygame.K_d)
            playerMovementKeysDown[pygame.K_d] = False # ser new value of False

    # qtyKeysUp = len(keysUp) # quantity 
    keysDown = [] # list of keys down
     
    for keyDownIndex in playerMovementKeysDown.keys():
        keyDownValue = playerMovementKeysDown[keyDownIndex]
        if(keyDownValue == True):
            keysDown.append(keyDownIndex) # append pygame index
    
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
        player.Update() # update the snake and move if enough time has passed. Func retunrs True if success
    # render snake below text in case player decides to go under text
    player.Render()
    player.RenderHitbox() # debugging
    if(game.end == False):
        pass
        #fruitController.updateFruits(playerSnake)
    #fruitController.renderFruits()
    if(game.end == False):
        player.RenderKillsText()
    else: # ended ==  True
        game.RenderEndGame(screen) 


    # flip() the display to put your work on screen
    pygame.display.flip()
    
    clock.tick(150)  # limits FPS 

print("closing")
pygame.quit()
