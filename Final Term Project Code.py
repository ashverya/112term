#ashverya sheth
#andrew id: ashverys

import pygame, sys, random
from pygame.locals import *
import math


class AshMath(object): #math class
    @staticmethod
    def arctan(x, y):
        if x > 0:
            return math.atan(-y/x)
        elif x < 0:
            return math.pi - math.atan(y/x)
        else: #x is 0
            return math.copysign(math.pi/2, -y)

    @staticmethod
    def xDirection(angle):
        angle = abs(angle) % (2*math.pi) #makes every angle between 0 and 2 pi.
        if angle > math.pi/2 and angle < 3*math.pi/2:
            return -1 
        elif angle == math.pi/2 or angle == 3*math.pi/2:
            return 0
        else:
            return 1

class ThingOnField(pygame.sprite.Sprite):
    def __init__(self, x, y, color, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.color = color
        self.radius = 10
        self.rect = pygame.Rect(x, y, self.radius*2, self.radius*2)
        (self.centerX, self.centerY) = (self.rect.x + self.rect.width/2.0, self.rect.y + self.rect.height/2.0)
        self.velocity = 0
        self.angle = math.pi

    #xDir = movement in x direction, y = movement in y direction
    def move(self, xDir, yDir): 
        if self.game.isLegalMove(self, xDir, yDir):
            self.rect.x += xDir
            self.rect.y += yDir
            return True
        return False

    def findCenter(self):
        return (self.rect.x+self.rect.width/2.0, self.rect.y+self.rect.height/2.0) 
        #returns center of player

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.rect.x + self.radius, 
            self.rect.y + self.radius), self.radius)

    def description(self):
        return "self.x =", self.x, "self.y =", self.y, "rect = ", self.rect

    def autoUpdateLocation(self): #updates ball when already is moving
        xDirection = round(self.velocity*math.cos(self.angle))
        yDirection = -round(self.velocity*math.sin(self.angle))
        self.move(xDirection, yDirection)

class WhitePartOfField(object):
    def __init__(self, game):
        self.game = game
        thickness = self.thickness = 3
        self.leftSideline = GoalOrSidelinesRect(0, 0, thickness, game.appHeight)
        self.rightSideline = GoalOrSidelinesRect(game.appWidth-thickness, 0, thickness, game.appHeight)
        self.upperSideline = GoalOrSidelinesRect(0, 0, game.appWidth, thickness)
        self.lowerSideline = GoalOrSidelinesRect(0, game.appHeight-thickness, game.appWidth, thickness)
        self.halfwayLine = GoalOrSidelinesRect(game.appWidth/2-thickness/2, 0, thickness, game.appHeight)

    def draw(self, screen):
        white = (255, 255, 255)
        thickness = self.thickness
        radiusThickness = self.thickness + 2
        radius = self.game.appWidth/12
        pygame.draw.rect(screen, white, self.leftSideline, thickness)
        pygame.draw.rect(screen, white, self.rightSideline, thickness)
        pygame.draw.rect(screen, white, self.upperSideline, thickness)
        pygame.draw.rect(screen, white, self.lowerSideline, thickness)
        pygame.draw.rect(screen, white, self.halfwayLine, thickness)
        pygame.draw.circle(screen, white, (self.game.appWidth/2, self.game.appHeight/2), radius, radiusThickness)

class Goal(object): #2 goals on the page
    def __init__(self, x, y, width, length):
        self.thickness = thickness = 3
        self.goalTop = GoalOrSidelinesRect(x, y, width, thickness) #top small part of goal
        self.goalBottom = GoalOrSidelinesRect(x, y + length, width, thickness)
        self.goalLeft = GoalOrSidelinesRect(x + width, y, thickness, length) #goal on left side of field
        self.goalRight = GoalOrSidelinesRect(x, y, thickness, length) #goal on right side of field.
        self.rect = pygame.Rect(x, y, width, length)

    def collidesWithBall(self, ball):
        if pygame.sprite.collide_circle(self.goalLeft, ball) or pygame.sprite.collide_circle(self.goalRight, ball): #scores goal yay 
            return True
        elif pygame.sprite.collide_circle(self.goalTop, ball) or pygame.sprite.collide_circle(self.goalBottom, ball): #hits off top/bottom
            ball.bounceOffTopOrBottom()
        return False

    def collidesWithPlayer(self, player):
        if pygame.sprite.collide_rect(self.goalTop, player) or pygame.sprite.collide_rect(self.goalBottom, player):
            return True
        return False


    def draw(self, screen):
        white = (255, 255, 255)
        pygame.draw.rect(screen, white, self.rect, self.thickness)

class GoalOrSidelinesRect(pygame.sprite.Sprite):
    def __init__(self, topLeftX, topLeftY, width, height):
        self.x = topLeftX
        self.y = topLeftY
        self.width = width
        self.height = height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

class Ball(ThingOnField):
    def __init__(self, x, y, color, game, ballImage, radius):
        ThingOnField.__init__(self, x, y, color, game)
        self.angle = math.pi*1.1 #starts off going left
        self.velocity = 5
        self.radius = radius
        self.maxVelocity = 5 #maximum velocity a ball can go at. 
        self.ballImage = ballImage
        self.angleToRotateBallAt = 0

    def draw(self, screen): #draws the ball with it already rotated
        if not(self.game.paused):
            self.angleToRotateBallAt += AshMath.xDirection(self.angle) #this rotates the ball 
        rotatedBallImage = pygame.transform.rotate(self.ballImage, self.angleToRotateBallAt)
        screen.blit(rotatedBallImage, (self.rect.x, self.rect.y))

    def bounceOffTopOrBottom(self):
        self.angle *= -1

    def bounceOffSides(self):
        self.angle = math.pi - self.angle

    def updateBallRect(self, centerX, centerY):
        (self.rect.x, self.rect.y) = (centerX - self.radius, centerY - self.radius)

class Player(ThingOnField):
    def __init__(self, x, y, color, game):
        ThingOnField.__init__(self, x, y, color, game)
        self.ball = None #starts with no ball
        self.counter = 0 #if counter is 0, then player can move
        self.currentImageIndex = 0
        self.rect = pygame.Rect(x, y, 40, 50)


    def move(self, xDir, yDir):
        if not(self.playerIsStunned()):
            if ThingOnField.move(self, xDir, yDir): #if actually moved
                self.velocity = (xDir**2+yDir**2)**0.5 #finding velocity (positive always)
                self.angle = AshMath.arctan(xDir, yDir)
                if self.ball != None:
                    self.ball.move(xDir, yDir) #ball moves just how the player moves

    def draw(self, screen):
        if self.game.tick % 5 == 0: #every second
            if self.currentImageIndex == 0:
                self.currentImageIndex = AshMath.xDirection(self.angle)
            else: 
                self.currentImageIndex = 0
        currentPlayerImage = self.game.stagesOfPerson[self.currentImageIndex]
        screen.blit(currentPlayerImage, (self.rect.x, self.rect.y))
        #pygame.draw.rect(screen, (0, 250, 0), self.rect)


        #call this when two players collide
    def updatePlayerDirectionOnCollision(self):
        scale = 1.2 #moves players away from each other by this factor
        xDirection = -self.velocity*math.cos(self.angle)
        yDirection = -self.velocity*math.sin(self.angle)
        xDirection = math.copysign(math.ceil(abs(xDirection)), xDirection)
        yDirection = math.copysign(math.ceil(abs(yDirection)), yDirection)
        self.move(xDirection*scale, yDirection*scale)

    def decreasePlayerCounter(self):
        if self.counter > 0:
            self.counter -= 1

    def stunsPlayer(self):
        self.counter = 10 #max number for counter

    def stunForever(self, infinity = 1000000): #this will stun a player for infinite time (longer than game time)
        self.counter = infinity

    def unstun(self): #unstuns the player
        self.counter = 0

    def playerIsStunned(self):
        return self.counter > 0 #returns True if player counter is not 0 (player should not be able to move)

class AIPlayer(Player):
    #this will move the AI PLAYER that is closest to the ball, to the ball.
    def moveAIPlayerToBall(self, ball):
        (AIcenterX, AIcenterY) = self.findCenter() #center of ai player
        (centerOfBallX, centerOfBallY) = ball.findCenter() #center of ball
        (xDistance, yDistance) = (centerOfBallX - AIcenterX, centerOfBallY - AIcenterY)
        self.angle = AshMath.arctan(xDistance, yDistance)
        self.velocity = 2.5 #not quite as fast as human players
        xDir = self.velocity*math.cos(self.angle)
        yDir = -self.velocity*math.sin(self.angle)
        self.move(xDir, yDir) #moves ai player towards the ball.

    def stunsPlayer(self):
        self.counter = 100 #ai players should be stunned longer

class Game(object):
    def initAnimation(self):
        self.splashScreen = True
        self.helpScreen = False
        self.appWidth = 800
        self.appHeight = 600
        x, y = 0, 0
        self.blue = (0, 0, 150) #rgb string
        self.red = (150, 0, 0)
        self.orange = (255, 165, 0)
        self.userScore = 0 #first team
        self.AIScore = 0 #second team
        self.screen = pygame.display.set_mode((self.appWidth, self.appHeight))
        self.createImages()
        #creating groups
        (self.ball_group, self.goals_group)  = (pygame.sprite.Group(), pygame.sprite.Group()) 
        #creating group that contains ball
        (self.players_group, self.players_list) = (pygame.sprite.Group(), []) 
        #creating group that contains players
        (self.AIplayers_group, self.AIplayers_list) = (pygame.sprite.Group(), []) 
        #creating AI players group
        self.createPlayersAndAddToGroups() #creates all the players on the field
        self.tick = 0 #ticks every timer fired
        self.keyIsPressed = False
        self.playerSpeed = 0
        (self.goalWidth, self.goalHeight) = (50, 100)
        self.leftGoal = Goal(0, self.appHeight/2-self.goalWidth, self.goalWidth, self.goalHeight) #x, y, width, height
        self.rightGoal = Goal(self.appWidth-self.goalWidth,self.appHeight/2-self.goalWidth, self.goalWidth, self.goalHeight)
        self.WhitePartOfField = WhitePartOfField(self)
        self.automaticMode = True #game starts off with game automatically selecting player
        self.paused = True
        self.gameOver = False
        self.framesPerSecond = 60
        self.timeLeft = 120 # given in seconds
        self.selectedPlayer = None
        self.power = 0 #power meter for power to kick the ball
        self.maxPower = 5 #maximum amount of power
        self.firstTouch = True
        self.freezeAngle = math.pi/2
        self.playerJustGotBall = False

    def createPlayersAndAddToGroups(self):
        (startLeft, startRight, width, scale, offset) = (100, 500, 100, 30, 20)
        for i in xrange(5): 
            if i < 3:
                newPlayer = Player(startLeft,2*startLeft+width*i,self.blue, self)
                newPlayer.add(self.players_group)
                self.players_list.append(newPlayer)
            elif i == 3:
                newPlayer = Player(2*startLeft,2*startLeft+offset*i, self.blue, self)
                newPlayer.add(self.players_group)
                self.players_list.append(newPlayer)
            elif i == 4:
                newPlayer = Player(2*startLeft,2*startLeft+scale+scale*i, self.blue, self)
                newPlayer.add(self.players_group)
                self.players_list.append(newPlayer)
        for i in xrange(5): #adding AI players here.
            if i < 3:
                newAIPlayer = AIPlayer(startRight+width, 2*width+width*i, self.orange, self)
                newAIPlayer.add(self.AIplayers_group)
                self.AIplayers_list.append(newAIPlayer)
            elif i == 3:
                newAIPlayer = AIPlayer(startRight, 2*width+offset*i, self.orange, self)
                newAIPlayer.add(self.AIplayers_group)
                self.AIplayers_list.append(newAIPlayer)
            elif i == 4:
                newAIPlayer = AIPlayer(startRight, 2*width+scale+scale*i, self.orange, self)
                newAIPlayer.add(self.AIplayers_group)
                self.AIplayers_list.append(newAIPlayer)

    def createImages(self): #creates all images
        (personWidth, personHeight) = (40, 50)
        self.runningLeftImage = pygame.image.load("runningleft.png").convert_alpha() 
        #http://thermtc.com/wp-content/uploads/2011/04/Running-icon.png
        self.runningLeftImage = pygame.transform.scale(self.runningLeftImage, 
            (personWidth, personHeight))
        self.runningRightImage = pygame.image.load("runningright.png").convert_alpha()
        #http://www.clker.com/cliparts/e/w/T/q/9/L/running-icon-on-transparent-background-hi.png
        self.runningRightImage = pygame.transform.scale(self.runningRightImage, 
            (personWidth, personHeight))
        self.restingImage = pygame.image.load("resting.png").convert_alpha() 
        #http://cdn.flaticon.com/png/256/46994.png
        self.restingImage = pygame.transform.scale(self.restingImage, 
            (personWidth, personHeight))
        self.stagesOfPerson = [self.restingImage, self.runningRightImage, 
        self.runningLeftImage]
        self.field = pygame.image.load("field.png").convert() #field is background
        #http://www.hdwallsource.com/light-green-background-31850.html
        self.field = pygame.transform.scale(self.field, (self.appWidth, 
            self.appHeight))
        ballRadius = 14    
        self.ballImage = pygame.image.load("soccerball.png").convert_alpha() #ball image 
        #http://franktorresblog.files.wordpress.com/2013/03/soccer-ball.jpg
        self.ballImage = pygame.transform.scale(self.ballImage, (ballRadius*2, 
            ballRadius*2))
        self.ball = Ball(self.appWidth/2, self.appHeight/2, self.red, self, 
            self.ballImage, ballRadius)
        self.splashScreenImage = pygame.image.load("splashscreen6.jpg") 
        #http://amagico.com/soccer-ball-wallpaper-hd-background-wallpaper-38-hd-wallpaper.html
        #using picfont.com to modify image
        self.splashScreenImage = pygame.transform.scale(self.splashScreenImage, 
            (self.appWidth, 3*self.appHeight/4))
        self.helpScreenImage = pygame.image.load("helpscreen3.jpg")
        self.helpScreenImage = pygame.transform.scale(self.helpScreenImage, 
            (self.appWidth, 3*self.appHeight/4))
        #http://totallytwitter.files.wordpress.com/2011/07/twitter3.png

    #this method is to find x direction
    @staticmethod
    def findAngleInSameXDirection(angle):
        scale = 100.0
        angle = abs(angle) % (2*math.pi) #makes every angle between 0 and 2 pi.
        if angle > math.pi/2 and angle < 3*math.pi/2:
            return random.randrange(int(scale*math.pi/2), int(scale*3*math.pi/2))/scale
            #need this because randrange only works for integers
        elif angle == math.pi/2 or angle == 3*math.pi/2:
            return random.choice([math.pi/2, -math.pi/2])
        else:
            return random.randrange(int(scale*-math.pi/2), int(scale*math.pi/2))/scale

    def onTimerFired(self):
        self.playerJustGotBall = False #player did not just get ball under possession
        self.tick += 1 #increment time by 1 
        if self.tick % self.framesPerSecond == 0: self.timeLeft -= 1 #every second
        if self.timeLeft == 0: self.gameOver = True #game is over if time runs out.
        self.handleBallWallCollision()
        self.ball.velocity *= 0.999 #friction
        #goes through user/ai players and checks collisions with everything
        self.checkUserPlayerCollisions() 
        self.checkAIPlayerCollisions()
        #selects the closest AI player to move towards the ball
        (AIPlayer, event) = (self.selectPlayer(self.AIplayers_group), self.event) 
        if AIPlayer.ball == None: #if AI player does not have ball then move ai player.
            AIPlayer.moveAIPlayerToBall(self.ball) #check if is legal later. 
        self.removesBallFromAIPlayers() #no ai player has the ball anymore
        if self.automaticMode: #selects player to move automatically
            (self.selectedPlayer, event) = (self.selectPlayer(self.players_group), self.event) 
        if self.keyIsPressed: #key is down
            self.keyControls(self.selectedPlayer)
        else: #player is not moving
            self.selectedPlayer.velocity = 0
        for otherPlayer in self.players_group: 
        #for every player not closest to ball, move in same direction as that player.
            if otherPlayer != self.selectedPlayer:
                self.moveUserTeammates(self.selectedPlayer, otherPlayer)
        selectedAIPlayer = self.selectPlayer(self.AIplayers_group)
        for otherAIPlayer in self.AIplayers_group:
            if otherAIPlayer != selectedAIPlayer:
                self.moveUserTeammates(selectedAIPlayer, otherAIPlayer)
        if self.checkIfScores(): #checks to see if either team scores
            self.resetAfterGoal() #resets ball/players if goal is scored
        canUpdateBall = True 
        #unless a player has possession of the ball, ball should be auto updated
        for player in self.players_group:
            if player.ball != None: #if no player has possession of the ball
                canUpdateBall = False
        if canUpdateBall:
            self.ball.autoUpdateLocation() 
            #updates ball's position if no player has the ball

    def moveUserTeammates(self, selectedPlayer, player):
        player.angle = Game.findAngleInSameXDirection(selectedPlayer.angle)
        player.velocity = selectedPlayer.velocity
        player.autoUpdateLocation() #makes rest of user's teammates move 


    def checkUserPlayerCollisions(self):
        for player in self.players_group:
            player.decreasePlayerCounter()
            (self.ball.centerX, self.ball.centerY) = self.ball.findCenter()
            (player.centerX, player.centerY) = player.findCenter()
            if player.ball == None and not(player.playerIsStunned()):
                if pygame.sprite.collide_circle(self.ball, player):
                    if self.firstTouch == False:
                        self.firstTouch = True
                        self.unstunAll()
                    self.ball.velocity = player.velocity
                    self.ball.angle = self.freezeAngle 
                    #this freezes the rotation so that ball does not rotate
                    self.givesBallToOnePlayer(player) 
                    #means that player has the game ball under possession
                    self.playerJustGotBall = True
                #else: self.power = 0 #resets power if no player has the ball.
            for otherPlayer in self.players_group: 
            #finding the second player to check for collision between 2 players
                if player != otherPlayer:
                    if pygame.sprite.collide_rect(player, otherPlayer): 
                    #2 players collide
                        self.playersCollide(player, otherPlayer)

    def checkAIPlayerCollisions(self):
        for AIPlayer in self.AIplayers_group:
            AIPlayer.decreasePlayerCounter()
            (AIPlayer.centerX, AIPlayer.centerY) = AIPlayer.findCenter()
            distance = math.hypot(self.ball.centerX - AIPlayer.centerX, 
            self.ball.centerY - AIPlayer.centerY) #my own collision detection
            if AIPlayer.ball == None and not(AIPlayer.playerIsStunned()):
                if distance <= AIPlayer.radius + self.ball.radius:
                    if self.playerJustGotBall:
                        AIPlayer.stunsPlayer() 
                        #stuns the ai player if the user player 
                        #just got possession of the ball
                    else:
                        self.givesBallToOnePlayer(AIPlayer) 
                        #gives ai player the ball. 
                        #stuns other players that have the ball currently.
                        if self.firstTouch == False:
                            self.firstTouch = True
                            self.unstunAll()
                        assert AIPlayer.ball == self.ball
                        self.AIplayerAndBallCollide(AIPlayer) 
                        #ai player kicks & changes direction of ball 
                        assert AIPlayer.ball == self.ball 
                        #ai player stil has the ball
                        self.power = 0 #player takes ball, player doesn't have it
            for otherPlayer in self.AIplayers_group:
             #finding the second player to check for collision between 2 players
                if AIPlayer != otherPlayer:
                    if pygame.sprite.collide_circle(AIPlayer, otherPlayer): 
                    #2 players collide
                        self.playersCollide(AIPlayer, otherPlayer)

    def handleBallWallCollision(self):
        (w, h) = (self.appWidth, self.appHeight)
        offset = 8 #for glitches in bouncing ball
        if (self.ball.rect.x <= offset) or (self.ball.rect.x + self.ball.rect.width >= w - offset):
            self.ball.bounceOffSides() #bounces off l/r walls
        if (self.ball.rect.y <= offset) or (self.ball.rect.y + self.ball.rect.height >= h - offset): 
            self.ball.bounceOffTopOrBottom()

    #this function switches off and on from manual to automatic mode
    def switchPlayersOnManualMode(self):
        if self.keys[K_1]:
            self.selectedPlayer = self.players_list[0]
        elif self.keys[K_2]:
            self.selectedPlayer = self.players_list[1]
        elif self.keys[K_3]:
            self.selectedPlayer = self.players_list[2]
        elif self.keys[K_4]:
            self.selectedPlayer = self.players_list[3]
        elif self.keys[K_5]:
            self.selectedPlayer = self.players_list[4]

    def keyControls(self, player): #logic for movement
        (xDir, yDir) = (0, 0)
        if not self.automaticMode: #if on manual mode
            self.switchPlayersOnManualMode()
        if self.keys[K_SPACE]: #power meter
            if self.splashScreen:
                self.splashScreen = False
            else:
                if player.ball != None: #power can be changed if player has ball
                    if self.power < self.maxPower: #max power is 5
                        self.power += 0.1
        if self.keys[K_a]:
            self.automaticMode = not(self.automaticMode) 
            #mode is either that player is selected for user or user selects player
        if self.keys[K_UP]:
            if self.isLegalMove(player, 0, -self.playerSpeed): #checks if it's legal to move
                 yDir = -self.playerSpeed
        if self.keys[K_DOWN]:
            if self.isLegalMove(player, 0, self.playerSpeed):
                yDir = self.playerSpeed
        if self.keys[K_LEFT]:
            if self.isLegalMove(player, -self.playerSpeed, 0):
                xDir = -self.playerSpeed
        if self.keys[K_RIGHT]:
            if self.isLegalMove(player, self.playerSpeed, 0): 
                xDir = self.playerSpeed
        if self.keys[K_6]:
            self.timeLeft = 10
        if player.ball != None and (self.keys[K_x] or self.keys[K_c]): #player kicks the ball or passes to another player
            self.ball.velocity = self.ball.maxVelocity + self.power
            self.removesBallFromAllPlayers()
            self.ball.angle = AshMath.arctan(xDir, yDir)
            if self.keys[K_c]: #passes the ball
                angleOfKeys = AshMath.arctan(xDir, yDir)
                smallestAngle = None
                for passPlayer in self.players_group:
                    if passPlayer != player:
                        differenceOfAngles = self.findDifferenceBetweenTwoAngles(player, passPlayer, angleOfKeys)
                        if smallestAngle == None or differenceOfAngles < smallestAngle:
                            smallestAngle = self.angleBetweenPlayers
                self.ball.angle = smallestAngle 
            self.power = 0
        else:
            player.move(xDir, yDir)
            if self.playerCollidesWithAnyGoal(player): #if a player collides with the goal, move it back real quick
                player.move(-xDir, -yDir)
        if self.keys[K_t]:
            self.removesBallFromAIPlayers()
            player.ball = self.ball

    #this function takes two players and returns the difference between the 
    #angle between the two players and the angle given
    #this is helpful for passing when trying to find smallest angle to pass ball
    def findDifferenceBetweenTwoAngles(self, player, passedToPlayer, angle):
        (passedToPlayerCenterX, passedToPlayerCenterY) = passedToPlayer.findCenter() #player who gets passed to
        (playerCenterX, playerCenterY) = player.findCenter() #player who passed
        x = passedToPlayerCenterX - playerCenterX
        y = passedToPlayerCenterY - playerCenterY
        self.angleBetweenPlayers = AshMath.arctan(x, y)
        return abs(self.angleBetweenPlayers - angle)

    #this function is called by key controls and returns True or False 
    def isLegalMove(self, movingObject, xDir, yDir):
        if movingObject.rect.x + movingObject.rect.width + xDir <= self.appWidth:
            if movingObject.rect.x + xDir >= 0:
                if movingObject.rect.y + movingObject.rect.height + yDir <= self.appHeight:
                    if movingObject.rect.y + yDir >= 0:
                        return True
        return False

    #this method resets all the players and ball after a goal is scored
    #needs to also include that the team that just lost possession is the team that can touch it first
    def resetAfterGoal(self):
        (centerOfFieldX, centerOfFieldY) = (self.appWidth/2, self.appHeight/2)
        (self.ball.rect.x, self.ball.rect.y) = (centerOfFieldX - self.ball.radius, 
        centerOfFieldY - self.ball.radius) #places ball in middle of field
        self.removesBallFromAllPlayers() #ball is no longer possessed by anyone
        self.ball.velocity = 0 #ball is at 0 velocity
        self.ball.angle = self.freezeAngle # freezes ball rotation here too
        (xPos, xScale, xOffset) = (100, 20, 200)
        (yPos, yOffset, yScale) = (500, 100, 30)
        for i in xrange(len(self.players_list)):
            if i < 3:
                (self.players_list[i].rect.x, self.players_list[i].rect.y) = (xPos, xOffset+xPos*i)
                (self.AIplayers_list[i].rect.x, self.AIplayers_list[i].rect.y) = (yPos+yOffset, xOffset+xPos*i)
            elif i == 3:
                (self.players_list[i].rect.x, self.players_list[i].rect.y) = (xOffset,xOffset+xScale*i)
                (self.AIplayers_list[i].rect.x, self.AIplayers_list[i].rect.y) = (yPos, xOffset+xScale*i)
            elif i == 4:
                (self.players_list[i].rect.x, self.players_list[i].rect.y) = (xOffset,xOffset+yScale*i)
                (self.AIplayers_list[i].rect.x, self.AIplayers_list[i].rect.y) = (yPos, (xOffset+yScale)+yScale*i)
        self.firstTouch = False #nobody has touched the ball since the last goal. 

    #returns True if ball and user player are colliding. returns False if not. 
    def ballAndPlayerAreColliding(self, player):
        if abs(self.ball.centerX - player.centerX) <= self.ball.radius + player.radius: 
        # if the ball and player are touching x direction
            if (self.ball.centerY - player.centerY) <= self.ball.radius + player.radius: 
            #if the ball and player are touching y direction
                return True
        return False

    #stuns an entire group of players
    def stunsGroup(self, group):
        for player in group:
            player.stunForever()

    #unstuns an entire group of players
    def unstunGroup(self, group):
        for player in group:
            player.unstun()

    #unstuns all groups of players
    def unstunAll(self):
        self.unstunGroup(self.players_group)
        self.unstunGroup(self.AIplayers_group)

    #returns True if either team has scored. returns False if no team has scored
    def checkIfScores(self):
        if self.rightGoal.collidesWithBall(self.ball): #user scores goal
            self.userScore += 1
            self.stunsGroup(self.players_group) #stuns user players after they score
            return True
        if self.leftGoal.collidesWithBall(self.ball): #AI player scores goal
            self.AIScore += 1
            self.stunsGroup(self.AIplayers_group) #stuns the ai players after they score
            return True
        return False

    #returns True if player collides with either goal. False if doesn't
    def playerCollidesWithAnyGoal(self, player):
        if self.leftGoal.collidesWithPlayer(player) or self.rightGoal.collidesWithPlayer(player):
            return True
        return False


    #this method selects the player that is closest to the ball.
    def selectPlayer(self, playerGroup):
        closestPlayer = None #initializes closest player
        closestPlayerDistance = None
        if playerGroup == self.players_group: group = self.players_group
        else: group = self.AIplayers_group 
        for player in group:
            (playerX, playerY) = (player.findCenter()) #center of player
            (ballX, ballY) = (self.ball.findCenter()) #center of ball
            distance = math.hypot(ballX-playerX, ballY-playerY)
            if closestPlayerDistance == None or distance < closestPlayerDistance: 
            #gets player of smallest distance from ball
                closestPlayerDistance = distance
                closestPlayer = player
        return closestPlayer

    #takes away possession of ball from a group
    def removesBallFromThisGroup(self, group, stunsPlayer = False):
        for player in group:
            if player.ball != None and stunsPlayer == True:
                player.stunsPlayer()
            player.ball = None

    #takes away ball from all the AI players only
    def removesBallFromAIPlayers(self, stunsPlayer = False):
        self.removesBallFromThisGroup(self.AIplayers_group, stunsPlayer) 
        #only stuns ai player if necessary

    #takes away ball from all players on the field (user and ai)
    def removesBallFromAllPlayers(self, stunsPlayer = False):
        self.removesBallFromAIPlayers(stunsPlayer) #takes away ball from AI players from other method
        self.removesBallFromThisGroup(self.players_group, stunsPlayer)

    #ball taken away from all players and given to specified player
    def givesBallToOnePlayer(self, player):
        assert player.playerIsStunned() == False
        #makes sure that player passed in is not stunned      
        self.removesBallFromAllPlayers(True) #stuns player from the beginning.
        player.ball = self.ball 
        #gives ball to the one player that has possession  
                

    #if a collision between 2 players happens!
    def playersCollide(self, player1, player2):
        player1.updatePlayerDirectionOnCollision()
        player2.updatePlayerDirectionOnCollision()

    #when an AI player and ball collide, AI player kicks in certain direction
    #based on where it is on the field
    def AIplayerAndBallCollide(self, player): 
        assert player.ball != None
        ball = player.ball
        offset = 30
        #min distance the ball can be from left side in order for AI to kick left
        ball.velocity = player.ball.maxVelocity 
        #ball is kicked so goes back to max velocity
        if self.ball.rect.x < offset: #if ball is too far on left
            ball.angle = random.randrange(int(100*-math.pi/2), 
            int(100*math.pi/2))/100.0 #kicks right
        elif self.ball.rect.y < offset: #player is too far up top
            ball.angle = random.randrange(int(100*math.pi), 
                int(100*2*math.pi))/100.0
        elif self.ball.rect.y + self.ball.rect.height > self.appHeight - offset: 
        #player is too far on bottom
            ball.angle = random.randrange(int(0),
            int(100*math.pi))/100.0 #kicks up
        else:
            ball.angle = random.randrange(int(100*math.pi/3.5), 
            int(100*3.5*math.pi/2))/100.0 #kicks left in most cases
       

    def drawSplashScreen(self):
        self.screen.fill((0,0,0))
        self.screen.blit(self.splashScreenImage, (0,self.appHeight/8))

    def drawHelpScreen(self):
        self.screen.fill((0,0,0))
        self.screen.blit(self.helpScreenImage, (0, self.appHeight/8))


    #this method returns a string that is used in game over 
    #when telling the user who wins
    def gameOverTextBasedOnWinner(self):
        if self.userScore > self.AIScore: #user wins
            return "Game over. You win!"
        elif self.userScore < self.AIScore: #user loses
            return "Game over. You lose!"
        else: #there was a tie
            return "Game over. There was a tie!"

    #this function is called by redrawAll. it draws the score & time left 
    #and game over text.
    def drawScoreAndTimeLeftAndGameOver(self):
        if self.gameOver: #if game is over, show game over screen
            gameOverBackgroundColor = (50, 0, 100)
            gameOverRect = pygame.Rect(0, 0, self.appWidth, self.appHeight) 
            pygame.draw.rect(self.screen, gameOverBackgroundColor, gameOverRect) 
            #draws rectangle over the screen
            font = pygame.font.Font(None, 40)
            gameOverString = self.gameOverTextBasedOnWinner()
            gameOverText = font.render(gameOverString, 1, (255, 255, 255))
            self.screen.blit(gameOverText, (self.appWidth/2 - 160, self.appHeight/4)) 
        else: #this happens throughout the game until game is over
            font = pygame.font.Font(None, 36) #sets font for score
            score = "score(you vs. computer): %d to %d" %(self.userScore, self.AIScore)
            scoreText = font.render(score, 1, (255,255,255)) #creates text for score
            self.screen.blit(scoreText, (self.appWidth/2+20, self.appHeight*(7/8.0)))
            #now draw time left:
            font = pygame.font.Font(None, 36)
            (minutes, seconds) = (self.timeLeft/60, self.timeLeft%60)
            timeLeftString = "time left: %d:%.2d" %(minutes, seconds)
            timeLeftText = font.render(timeLeftString, 1, (255, 255, 255))
            self.screen.blit(timeLeftText, (self.appWidth/2+20, self.appHeight*(15/16.0)))

    #draws power meter depending on how much power there is
    def drawPowerMeter(self):
        (red, white) = ((250, 0, 0), (255, 255, 255)) #rgb strings for colors
        (xPos, yPos, height) = (self.appWidth/4, self.appHeight*10/11.0, 30)
        (widthOfRect, heightOfRect, fontSize) = (30*self.maxPower, 30, 36)
        #draws white surrounding power rectangle
        whitePowerMeterRect = pygame.Rect(xPos, yPos, widthOfRect, heightOfRect)
        pygame.draw.rect(self.screen, white, whitePowerMeterRect, 1)
        if self.power != 0: #only draws power if power is not 0
            #draws actual power depending on how much there is 
            redPowerMeterRect = pygame.Rect(xPos, yPos, self.power*30, height)
            pygame.draw.rect(self.screen, red, redPowerMeterRect) #draws red power meter        
        #draws power text
        font = pygame.font.Font(None, fontSize) #sets font for power meter
        scoreText = font.render("POWER", 1, white) #creates text for power meter
        self.screen.blit(scoreText, (xPos + widthOfRect/5, yPos + 3))

    def drawPlayers(self):
        color = blue = (0, 0, 250)
        red = (250, 0, 0)
        playerNum = 1
        for player in self.players_list:
            if player == self.selectedPlayer: color = red
            else: color = blue   
            player.draw(self.screen)
            font = pygame.font.Font(None, 36) #sets font for number
            text = font.render(str(playerNum), 1, color) #creates text for number
            self.screen.blit(text, (player.rect.x, player.rect.y)) #puts number on each player
            playerNum += 1 
        for AIPlayer in self.AIplayers_group:
            AIPlayer.draw(self.screen)

    def redrawAll(self):
        if self.splashScreen:
            self.drawSplashScreen()
        elif self.helpScreen:
            self.drawHelpScreen()
        else:
            self.screen.blit(self.field, (0, 0))
            self.drawScoreAndTimeLeftAndGameOver() #draws score and time left
            self.drawPowerMeter()
            self.leftGoal.draw(self.screen)
            self.rightGoal.draw(self.screen)
            self.WhitePartOfField.draw(self.screen)
            self.drawPlayers()
            self.ball.draw(self.screen)
        pygame.display.update() #refreshes/updates screen

    #called when self.keyIsPressed is true. this allows to hold down key
    def onKeyPressed(self):
        self.keyIsPressed = True #players can now move

    def run(self):
        pygame.init()
        self.initAnimation()
        (w, h) = self.appWidth, self.appHeight
        clock = pygame.time.Clock()
        pygame.display.update()
        self.playerSpeed = 6
        while True:
            clock.tick(self.framesPerSecond) #60 frames per second
            for self.event in pygame.event.get(): #in every event that happens
                if self.event.type == pygame.QUIT: #lets us exit out of the game
                    sys.exit()
                self.keys = pygame.key.get_pressed() #keys that are held down
                self.onKeyPressed()
                if self.keys[K_p] or self.keys[K_h]: #paused
                    self.paused = not(self.paused)
                    if self.keys[K_h] and not self.splashScreen:
                        self.helpScreen = not(self.helpScreen)
                if self.keys[K_SPACE]:
                    self.splashScreen = False
                    self.paused = False
                if self.keys[K_r]:
                    self.run() 
                    #restarts game. when game is over we can stll press r key
            if not self.paused and not self.gameOver: #only runs if not paused
                self.onTimerFired()
            self.redrawAll()

Game().run()

