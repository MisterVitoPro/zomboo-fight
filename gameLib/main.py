'''Created on May 24, 2011

@author: Anthony D'Alessandro
'''
import pygame, random
import dataFiles, sprites, pickups, player, zombieSpawn, UI_HUD, sGroups, Levels
pygame.init()

class game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("ZOMBOO")
        self.spawnRate = random.randrange(10, 31)
        
        self.makeSprites()
        sGroups.staticSprites.draw(self.screen)
        self.mainLoop()
        
    def mainLoop (self):
        self.background = pygame.image.load(dataFiles.gamefieldBG).convert()
        timer = 0
        timerSpawn = 0
        timerPickup = 0
        zombieLvl = 0
        zombieSMin = 60
        zombieSMax = 90
        clock = pygame.time.Clock()
        keepGoing = True
        while keepGoing:
            clock.tick(30)
            pygame.mouse.set_visible(False)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    keepGoing = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        keepGoing = False
            
            timerPickup += 1
            if timerPickup >= 150:
                self.pickups()
                timerPickup = 0
            
            timer += 1
            if timer >= self.spawnRate:
                    self.spawnZombie(self.zombieSpawner.rect. center)
                    timer = 0
                    self.spawnRate = random.randrange (zombieSMin, zombieSMax)
            
            timerSpawn += 1        
            if timerSpawn >= (random.randrange(10*30, 15*30)):
                self.zombieSpawner = zombieSpawn.zombieSpawner (30)
                sGroups.UISprites.add(self.zombieSpawner)
                timerSpawn = 0
                zombieLvl += 1
                zombieSMin -= 6
                zombieSMax -= 6
                
            self.clearGroups()
            self.updateGroups()
            self.drawGroups()
            
            pygame.display.flip()
            
        pygame.mouse.set_visible(True)

    def spawnZombie(self, pos):
        zNum = random.randrange(1, 12)
        if zNum <= 11:
            zombie = sprites.Zombie(dataFiles.zombie1, pos)
            sGroups.zombieSprites.add(zombie)
        elif zNum > 13:
            bigZombie = sprites.BigZombie(dataFiles.zombieBig, pos)
            sGroups.zombieSprites.add(bigZombie)
        
    def pickups (self):   
        medkitSpawn = random.randrange (1, 101)
        shotgunSpawn = random.randrange (1, 101)    
        mp5Spawn = random.randrange (1, 101)
        clipSpawn = random.randrange(1, 101)
        grenadeSpawn = random.randrange(1, 101)
#        turretSpawn = random.randrange(1, 101)
#        
#        if turretSpawn <= 5:
#            turret = pickups.TurretPickup(dataFiles.turretIm)
#            sGroups.powerupSprites.add(turret)
        
        if medkitSpawn >= 90:
            food = pickups.foodPickup(dataFiles.foodIm)
            sGroups.powerupSprites.add(food)
        
        if medkitSpawn <= 10:
            medkit = pickups.Medkit (dataFiles.healthPackIm)
            sGroups.powerupSprites.add(medkit)
            
        if medkitSpawn >= 95:
            bazooka = pickups.RocketLauncher(dataFiles.bazookaIm)
            sGroups.powerupSprites.add(bazooka)
            
        if grenadeSpawn <= 10:
            grenadePick = pickups.grenadePickup(dataFiles.grenadeIm)
            sGroups.powerupSprites.add(grenadePick)
        
        if shotgunSpawn <= 10:
            shotgun = pickups.shotgunPickup (dataFiles.shotgunIm)
            sGroups.powerupSprites.add(shotgun)
        
        if mp5Spawn <= 10:
            mp5 = pickups.mp5Pickup (dataFiles.mp5Im)
            sGroups.powerupSprites.add(mp5)
            
        elif mp5Spawn >= 90:
            flamethrower = pickups.flameThrower(dataFiles.flamethrowerIm)
            sGroups.powerupSprites.add(flamethrower)
        
        if clipSpawn <= 20:
            clipPickup = pickups.ClipPickup(dataFiles.clipIm)
            sGroups.powerupSprites.add(clipPickup)
     
    def makeSprites(self):
#        level = Levels.Level(dataFiles.buildingWallsIm)
        
        self.player1 = player.Player(dataFiles.dude1Im, 1)
        sGroups.allySprites.add(self.player1)
        
        self.player2 = "none"
        
        if sprites.jCount == 2:
            self.player2 = player.Player(dataFiles.dude2Im, 2)
            sGroups.allySprites.add(self.player2)
            
            UIboard = sprites.UI(self.player2)
            sGroups.UISprites.add(UIboard)
            
            lasersight = sprites.LaserSight((dataFiles.laserSightIm), self.player2)
            sGroups.laserSprites.add(lasersight)
            
            
        
        UIboard = sprites.UI(self.player1)
        sGroups.textSprites.add(UIboard)
        
        healthBar = UI_HUD.healthBar(self.player1)
        sGroups.UIBarSprites.add(healthBar)
        
        lasersight = sprites.LaserSight((dataFiles.laserSightIm), self.player1)
        sGroups.laserSprites.add(lasersight)
        
        self.zombieSpawner = zombieSpawn.zombieSpawner (21)
        sGroups.UISprites.add(self.zombieSpawner)
    
    def clearGroups(self):
        sGroups.UISprites.clear(self.screen, self.background)
        sGroups.textSprites.clear(self.screen, self.background)
        sGroups.allySprites.clear(self.screen, self.background)
        sGroups.zombieSprites.clear(self.screen, self.background)
        sGroups.bulletSprites.clear(self.screen, self.background)
        sGroups.bombSprites.clear(self.screen, self.background)
        sGroups.fireSprites.clear(self.screen, self.background)
        sGroups.splatSprites.clear(self.screen, self.background)
        sGroups.laserSprites.clear(self.screen, self.background)
        sGroups.turretSprites.clear(self.screen, self.background)
        sGroups.UIBarSprites.clear(self.screen, self.background)
        sGroups.powerupSprites.clear(self.screen, self.background)
        sGroups.staticSprites.clear(self.screen, self.background)
        
    def updateGroups(self):
        sGroups.allySprites.update(sGroups.zombieSprites, sGroups.powerupSprites, sGroups.bombSprites)
        sGroups.zombieSprites.update(sGroups.bulletSprites, sGroups.fireSprites, self.player1, self.player2)
        sGroups.UISprites.update()
        sGroups.bulletSprites.update(sGroups.splatSprites, sGroups.fireSprites)
        sGroups.bombSprites.update(sGroups.fireSprites)
        sGroups.fireSprites.update()
        sGroups.splatSprites.update()
        sGroups.laserSprites.update()
        sGroups.powerupSprites.update()
        sGroups.turretSprites.update()
        sGroups.staticSprites.update()
        sGroups.UIBarSprites.update()
        sGroups.textSprites.update()
        
    def drawGroups(self):
        self.screen.blit(self.background, (0, 0))
        sGroups.powerupSprites.draw(self.screen)
        sGroups.allySprites.draw(self.screen)
        sGroups.zombieSprites.draw(self.screen)
        sGroups.bulletSprites.draw(self.screen)
        sGroups.bombSprites.draw(self.screen)
        sGroups.fireSprites.draw(self.screen)
        sGroups.laserSprites.draw(self.screen)
        sGroups.splatSprites.draw(self.screen)
        sGroups.turretSprites.draw(self.screen)
        sGroups.staticSprites.draw(self.screen)
        sGroups.UISprites.draw(self.screen)
        sGroups.UIBarSprites.draw(self.screen)
        sGroups.textSprites.draw(self.screen)
        
        
def menu():
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("ZOMBOO")
    
    background = pygame.image.load(dataFiles.mainMenuIm)
    screen.blit(background, (0, 0))
    
    keepGoing = 1
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)
    while keepGoing == 1:
        background = pygame.image.load(dataFiles.mainMenuIm)
        screen.blit(background, (0, 0))
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = 0
                donePlaying = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    keepGoing = 0
                    donePlaying = True
                if event.key == pygame.K_SPACE:
                    keepGoing = 0
                    donePlaying = False
        
        pygame.display.flip()
    return donePlaying
def main():
    donePlaying = False
    while not donePlaying:
        donePlaying = menu()
        if not donePlaying:
            game()
                       
if __name__ == "__main__":
    main()