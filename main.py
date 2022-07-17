import time
from invader_class import *
import neat
import random
import threading

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


def make_game(ge, config, display=False):
    MAIN_FONT = pygame.font.SysFont("comicsans", 30)
    
    print('generating another bot')
    
    level = 0
    score = 0    
    
    # create game
    
    if display:
        win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        pygame.display.set_caption("Space Invader")
        clock = pygame.time.Clock()
    else:
        stand_still_counter = 0
        last_position = (300, 650)
        corner_counter = 0
        start = time.time()
        
    background = Background()
    
    enemies = []
    wave_length = 5
    enemy_vel = [2, 3, 4]
    
    net = neat.nn.FeedForwardNetwork.create(ge, config)
    player = Player(300, 650, PLAYER_VEL)
    if not display:
        ge.fitness = 0
    # main game loop
    running = True
    while running:
        if display:
            clock.tick(FPS)

        if len(enemies) == 0: # level up
            if not display:
                ge.fitness += 10
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

        
        # input neurons
        l = []
        for enemy in enemies:
            for laser in enemy.lasers:
                l.append((laser, sqr_distance(laser, player)))
            l.append((enemy, sqr_distance(enemy, player)))
            l.sort(key=lambda x : x[1], reverse=False) # ascending
        
        obj1 = (0, 0, 0)
        obj2 = (0, 0, 0)
        obj3 = (0, 0, 0)
        obj4 = (0, 0, 0)
        obj5 = (0, 0, 0)
        if len(l) > 0:
            obj1 = (l[0][0].x, l[0][0].y, l[0][0].is_laser())
        if len(l) > 1:
            obj2 = (l[1][0].x, l[1][0].y, l[1][0].is_laser())
        if len(l) > 2:
            obj3 = (l[2][0].x, l[2][0].y, l[2][0].is_laser())
        if len(l) > 3:
            obj4 = (l[3][0].x, l[3][0].y, l[3][0].is_laser())
        if len(l) > 4:
            obj5 = (l[4][0].x, l[4][0].y, l[4][0].is_laser())
        if not display:
            # if player is too close to enemy => punish     
            # if (obj1[0] - player.x)**2 + (obj1[1] - player.y)  < 1: ge.fitness -= 1
            # if (obj2[0] - player.x)**2 + (obj2[1] - player.y)  < 1: ge.fitness -= 1
            # if (obj3[0] - player.x)**2 + (obj3[1] - player.y)  < 1: ge.fitness -= 1
            # if (obj4[0] - player.x)**2 + (obj4[1] - player.y)  < 1: ge.fitness -= 1
            # if (obj5[0] - player.x)**2 + (obj5[1] - player.y)  < 1: ge.fitness -= 1
            
            # if stay in the corner for too long => punish
            if player.x < 50 or player.x > WIN_WIDTH - 80:
                corner_counter += 1
            else:
                corner_counter -= 40
                if corner_counter < 0: corner_counter == 0
            if corner_counter > 80:
                ge.fitness -= 10
                # corner_counter == 0
            
            if player.x == last_position[0] and player.y == last_position[1]:
                stand_still_counter += 1
            else:
                stand_still_counter -= 20
                if stand_still_counter < 0: stand_still_counter == 0
            
            if stand_still_counter > 40:
                ge.fitness -= 10
                # stand_still_counter == 0
            
        outputs = net.activate((player.x,
                                obj1[0],
                                obj2[0],
                                obj3[0],
                                obj4[0],
                                obj5[0]))
        
        directions  = [0, 0]
        if outputs[0] > 0.5: # left
            directions[0] -= 1
        if outputs[1] > 0.5: # right
            directions[0] += 1
        # if outputs[2] > 0.5: # up
        #     directions[1] -= 1
        # if outputs[3] > 0.5: # down
        #     directions[1] += 1
        # if outputs[4] > 0.5: # shoot
        #     player.shoot(PLAYER_LASER_VEL)
            
        player.move(directions[0], directions[1])

        
        # not needed when implementing neural network
        if display:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        
        # check collision
        for enemy in enemies:
            for laser in enemy.lasers:
                if collide(player, laser): # die
                    if not display:
                        ge.fitness -= 10
                        running = False
                    break
            if collide(player, enemy):
                if not display:
                    ge.fitness -= 10
                    running = False
                break
            
        
        # enemy out of screen
        for i, enemy in enumerate(enemies):
            if enemy.is_off_screen():
                if not display:
                    ge.fitness += 0.5 # reward for let enemy pass
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
                    if not display:
                        ge.fitness += 1 # reward for shooting down the enemy
                    break
        
        if display:
            background.move()
            main_draw(win, background, level, score, player, enemies)
        else:   
            stop = time.time()
            if stop - start > 20:
                break 

def main(genomes, config):
    global gen
    
    gen += 1
    
    # create players and their associated neural network
    threads = []
    for _, ge in genomes:
        thread = threading.Thread(target=make_game, args=(ge, config))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    
def run(path):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                path)
    
    # population
    p = neat.Population(config)
    
    # stats reporter
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 20)
    
    make_game(winner, config, True) # play test
    
if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
    pygame.quit()