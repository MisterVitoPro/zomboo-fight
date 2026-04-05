"""ZOMBOO - Main game loop and menu.

Created 2011 by Anthony D'Alessandro.
"""
import pygame, random
import dataFiles, sprites, pickups, player, zombieSpawn, UI_HUD, sGroups
pygame.init()

# P2-009: This class is a monolithic "God class" that owns the game loop, spawn logic,
# pickup spawning, sprite management, and drawing. Future refactoring should split
# these responsibilities into separate modules (e.g. GameLoop, SpawnManager, Renderer).
class game:
    def __init__(self):
        self.screen = pygame.display.set_mode((dataFiles.SCREEN_WIDTH, dataFiles.SCREEN_HEIGHT))
        pygame.display.set_caption("ZOMBOO")
        self.spawnRate = random.randrange(10, 31)
        
        sGroups.empty_all()
        self.make_sprites()
        sGroups.staticSprites.draw(self.screen)
        self.main_loop()
        
    def main_loop (self):
        self.background = pygame.image.load(dataFiles.gamefieldBG).convert()
        timer = 0
        timerSpawn = 0
        timerPickup = 0
        zombieLvl = 0
        zombieSMin = 60
        zombieSMax = 90
        clock = pygame.time.Clock()
        keepGoing = True
        gameOverTimer = 0
        nextSpawnThreshold = random.randrange(10 * dataFiles.FPS, 15 * dataFiles.FPS)
        pygame.mouse.set_visible(True)
        while keepGoing:
            ms = clock.tick(dataFiles.FPS)
            dt = ms / (1000.0 / dataFiles.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    keepGoing = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        keepGoing = False

            if self.player1.dead:
                gameOverTimer += 1
                if gameOverTimer >= 9 * dataFiles.FPS:
                    keepGoing = False

            timerPickup += 1
            if timerPickup >= 150:
                self.pickups()
                timerPickup = 0

            timer += 1
            if timer >= self.spawnRate:
                    self.spawn_zombie(self.zombie_spawner.rect.center)
                    timer = 0
                    self.spawnRate = random.randrange(zombieSMin, zombieSMax)

            timerSpawn += 1
            if timerSpawn >= nextSpawnThreshold:
                self.zombie_spawner = zombieSpawn.ZombieSpawner(30)
                sGroups.UISprites.add(self.zombie_spawner)
                timerSpawn = 0
                zombieLvl += 1
                zombieSMin = max(zombieSMin - 6, 5)
                zombieSMax = max(zombieSMax - 6, 10)
                nextSpawnThreshold = random.randrange(10 * dataFiles.FPS, 15 * dataFiles.FPS)

            self.update_groups(dt)
            self.draw_groups()

            pygame.display.flip()

        pygame.mouse.set_visible(True)

    def spawn_zombie(self, pos):
        zNum = random.randrange(1, 13)
        if zNum <= 11:
            zombie = sprites.Zombie(dataFiles.zombie1, pos)
            sGroups.zombieSprites.add(zombie)
        else:
            bigZombie = sprites.BigZombie(dataFiles.zombieBig, pos)
            sGroups.zombieSprites.add(bigZombie)
        
    def pickups (self):
        # P2-008: Each spawn roll is independent -- multiple pickups can appear in one call.
        # medkitSpawn drives three separate if checks (food >= 90, medkit <= 10, bazooka >= 95),
        # so those can all trigger in the same call. mp5Spawn uses if/elif so MP5 and
        # Flamethrower are mutually exclusive. This is intentional game-balance behavior.
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
            food = pickups.FoodPickup(dataFiles.foodIm)
            sGroups.powerupSprites.add(food)
        
        if medkitSpawn <= 10:
            medkit = pickups.Medkit (dataFiles.healthPackIm)
            sGroups.powerupSprites.add(medkit)
            
        if medkitSpawn >= 95:
            bazooka = pickups.RocketLauncher(dataFiles.bazookaIm)
            sGroups.powerupSprites.add(bazooka)
            
        if grenadeSpawn <= 10:
            grenadePick = pickups.GrenadePickup(dataFiles.grenadeIm)
            sGroups.powerupSprites.add(grenadePick)
        
        if shotgunSpawn <= 10:
            shotgun = pickups.ShotgunPickup (dataFiles.shotgunIm)
            sGroups.powerupSprites.add(shotgun)
        
        if mp5Spawn <= 10:
            mp5 = pickups.Mp5Pickup (dataFiles.mp5Im)
            sGroups.powerupSprites.add(mp5)
            
        elif mp5Spawn >= 90:
            flamethrower = pickups.FlameThrower(dataFiles.flamethrowerIm)
            sGroups.powerupSprites.add(flamethrower)
        
        if clipSpawn <= 20:
            clipPickup = pickups.ClipPickup(dataFiles.clipIm)
            sGroups.powerupSprites.add(clipPickup)
     
    def make_sprites(self):
        
        self.player1 = player.Player(dataFiles.dude1Im, 1)
        sGroups.allySprites.add(self.player1)
        
        self.player2 = None
        
        if sprites.jCount == 2:
            self.player2 = player.Player(dataFiles.dude2Im, 2)
            sGroups.allySprites.add(self.player2)
            
            UIboard = sprites.UI(self.player2)
            sGroups.UISprites.add(UIboard)
            
            lasersight = sprites.LaserSight((dataFiles.laserSightIm), self.player2)
            sGroups.laserSprites.add(lasersight)
            
            
        
        UIboard = sprites.UI(self.player1)
        sGroups.textSprites.add(UIboard)
        
        health_bar = UI_HUD.HealthBar(self.player1)
        sGroups.UIBarSprites.add(health_bar)
        
        lasersight = sprites.LaserSight((dataFiles.laserSightIm), self.player1)
        sGroups.laserSprites.add(lasersight)
        
        self.zombie_spawner = zombieSpawn.ZombieSpawner (21)
        sGroups.UISprites.add(self.zombie_spawner)
    
    def update_groups(self, dt=1.0):
        sGroups.allySprites.update(sGroups.zombieSprites, sGroups.powerupSprites, sGroups.bombSprites, dt)
        sGroups.zombieSprites.update(sGroups.bulletSprites, sGroups.fireSprites, self.player1, self.player2, dt)
        sGroups.UISprites.update()
        sGroups.bulletSprites.update(sGroups.splatSprites, sGroups.fireSprites, dt)
        sGroups.bombSprites.update(sGroups.fireSprites, dt=dt)
        sGroups.fireSprites.update()
        sGroups.splatSprites.update()
        sGroups.laserSprites.update()
        sGroups.powerupSprites.update()
        sGroups.turretSprites.update()
        sGroups.staticSprites.update()
        sGroups.UIBarSprites.update()
        sGroups.textSprites.update()
        
    def draw_groups(self):
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
    screen = pygame.display.set_mode((dataFiles.SCREEN_WIDTH, dataFiles.SCREEN_HEIGHT))
    pygame.display.set_caption("ZOMBOO")
    
    background = pygame.image.load(dataFiles.mainMenuIm)
    screen.blit(background, (0, 0))
    
    keepGoing = 1
    donePlaying = True
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)
    while keepGoing == 1:
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