from invader_class import *
import neat
import random

gen = 0

def main_draw(win, bg, level, score, player, enemies):
    # draw background
    bg.draw(win)
    
    # draw text
    lives_label = MAIN_FONT.render(f"Level: {level}", 1, (255, 255, 255))
    level_label = MAIN_FONT.render(f"score: {score}", 1, (255, 255, 255))
    win.blit(lives_label, (10, 10))
    win.blit(level_label, (WIN_WIDTH - level_label.get_width() - 10, 10))
    
    # draw enemies
    for enemy in enemies:
        for laser in enemy.lasers:
            laser.draw(win)
        enemy.draw(win)
    
    # draw player
    player.draw(win)
    for laser in player.lasers:
        laser.draw(win)
    
    pygame.display.update()



def main():
    global gen
    
    level = 0
    score = 0    
    
    # create game
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Space Invader")
    
    background = Background()
    clock = pygame.time.Clock()
    
    enemies = []
    wave_length = 5
    enemy_vel = [2, 3, 4]
    
    player = Player(300, 650, PLAYER_VEL)
    # main game loop
    running = True
    while running:
        clock.tick(FPS)
        if len(enemies) == 0: # level up
            level += 1
            wave_length += 5
            background.vel += 1
            if wave_length > MAX_ENEMIES_PER_WAVE:
                wave_length = MAX_ENEMIES_PER_WAVE
                background.vel -= 1
            if(enemy_vel[2] < MAX_ENEMY_VEL):
                enemy_vel = [i + 1 for i in enemy_vel]
            
            # spawn enemies
            for i in range(wave_length):
                enemy = Enemy(random.randrange(0, WIN_WIDTH-50), random.randrange(-1500, -100), 
                                enemy_vel[random.randrange(0, 2)],                
                                random.choice(["red", "green", "blue"]))
                enemies.append(enemy)
        
        # not needed when implementing neural network
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # user input
        keys = pygame.key.get_pressed()
        directions = [0, 0]
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            directions[0] -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            directions[0] += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            directions[1] -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            directions[1] += 1
        if keys[pygame.K_SPACE]:
            player.shoot(PLAYER_LASER_VEL)
        
        player.move(directions[0], directions[1])
        
        # check collision
        for enemy in enemies:
            for laser in enemy.lasers:
                if collide(player, laser): # die
                    running = False
                    break
            if collide(player, enemy):
                running = False
                break
            
        
        # enemy out of screen
        for i, enemy in enumerate(enemies):
            if enemy.is_off_screen():
                score += 1
                enemies.pop(i)
            else:
                enemy.move()
                for laser in enemy.lasers:
                    laser.move(1)
                chance = random.randrange(1, 100)
                if(chance <= 15 and enemy.y > 0 + enemy.ship_img.get_height()):
                    enemy.shoot(ENEMY_LASER_VEL)
            
        for x, laser in enumerate(player.lasers):
            laser.move(-1)
            for i, enemy in enumerate(enemies):
                if collide(laser, enemy):
                    enemies.pop(i)
                    player.lasers.pop(x)
                    score += 5
                    break 
                
        background.move()
        main_draw(win, background, level, score, player, enemies)
    

    
if __name__ == '__main__':
    main()
    pygame.quit()