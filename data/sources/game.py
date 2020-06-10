import pygame
from pygame.locals import *
from random import choice

import time

from data.sources.files import Files
Files.load()

from data.sources.player import Player
from data.sources.enemy import Child_Enemy, Boss_Enemy
from data.sources.ground import Ground
from data.sources.shot import Shot
from data.sources.npc import Healer, Alchemist
from data.sources.screen import Screen

get_path = Files.get_full_path
play_sound = Files.play_sound

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(20)

# constants
FPS = 60

BLACK = (0, 0, 0)
GREEN = (2, 201, 55)
RED = (201, 2, 2)
PINK = (255, 0, 200)
WHITE = (255, 255, 255)
YELLOW = (237, 233, 0)

SCREEN_HEIGHT, SCREEN_WIDTH = 500, 900

class Game:
    
    def __init__(self):
        self.display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF)
        
        self.start_screen = Screen(WHITE)
        self.pause_screen = Screen(WHITE)
        self.game_over_screen = Screen(WHITE)
        
        self.player = Player()
        self.healer = Healer()
        self.alchemist = Alchemist()
        self.ground = Ground()
        
        self.boss_sprites = pygame.sprite.Group()
        self.child1_sprites = pygame.sprite.Group()
        self.child2_sprites = pygame.sprite.Group()
        
        self.clock = pygame.time.Clock()
        self.died_bosses = {}
        self.mouse_pos = (0, 0)
        
        self.child1_make_timer = 700
        self.child2_make_timer = 600
    
        self.state = 'start'
        
        self.show_shooting_power = False
        
    def setup(self):
        image_path = get_path('images', 'icon')
        icon = pygame.image.load(image_path)
        pygame.display.set_icon(icon)
        pygame.display.set_caption('Todd and his friends')
        
        self.ground.make_voids()
        self.ground.make_swamps()
        self.ground.make_trees()
        self.ground.make_decorations()
        self.ground.make_enemy_born_places()
        self.ground.make_teleport_places()
        
        boss_enemy1 = Boss_Enemy('bloody')
        boss_enemy1.init_position(self.ground.rect)
        boss_enemy2 = Boss_Enemy('wiz')
        boss_enemy2.init_position(self.ground.rect)
        
        self.boss_sprites = pygame.sprite.Group()
        self.boss_sprites.add(boss_enemy1)
        self.boss_sprites.add(boss_enemy2)
        
        ground_rect = self.ground.rect
        
        child1_enemy = Child_Enemy('bloody')
        child1_enemy.born(ground_rect)
        child1_enemy2 = Child_Enemy('bloody')
        child1_enemy2.born(ground_rect)
        
        self.child1_sprites.add(child1_enemy)
        self.child1_sprites.add(child1_enemy2)
        
        child2_enemy = Child_Enemy('wiz')
        child2_enemy.born(ground_rect)
        
        self.child2_sprites.add(child2_enemy)
        
        # background sound
        music_path = get_path('sounds', 'loops', 'Thought-Soup')
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(loops=-1)
        
    def make_screens(self):
        folder_path = get_path('images', 'screens', 'start', 'bg_gif')
        gif_pos = (SCREEN_WIDTH // 2, 75)
        self.start_screen.make_gif(folder_path, 70, gif_pos)
        
        start_btn = {
            'id': 's',
            'size': (SCREEN_WIDTH, 250),
            'position': (SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 2) + 25),
            'color': GREEN,
            'text': 'START',
            'text_size': 80,
        }
        self.start_screen.make_button(start_btn['id'],
                                start_btn['size'],
                                start_btn['position'],
                                start_btn['color'],
                                start_btn['text'],
                                start_btn['text_size'])
        
        exit_btn = {
            'id': 'e',
            'size': (SCREEN_WIDTH, 100),
            'position': (SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 2) + 200),
            'color': RED,
            'text': 'EXIT',
            'text_size': 80,
        }
        self.start_screen.make_button(exit_btn['id'],
                                exit_btn['size'],
                                exit_btn['position'],
                                exit_btn['color'],
                                exit_btn['text'],
                                exit_btn['text_size'])
        
        resume_btn = {
            'id': 'r',
            'size': (SCREEN_WIDTH, SCREEN_HEIGHT // 2),
            'position': (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4),
            'color': YELLOW,
            'text': 'RESUME',
            'text_size': 70,
        }
        self.pause_screen.make_button(resume_btn['id'],
                                resume_btn['size'],
                                resume_btn['position'],
                                resume_btn['color'],
                                resume_btn['text'],
                                resume_btn['text_size'])
        
        main_menu_btn = {
            'id': 'm',
            'size': (SCREEN_WIDTH, SCREEN_HEIGHT // 2),
            'position': (SCREEN_WIDTH // 2, 3 * (SCREEN_HEIGHT // 4)),
            'color': PINK,
            'text': 'MAIN MENU',
            'text_size': 70,
        }
        self.pause_screen.make_button(main_menu_btn['id'],
                                main_menu_btn['size'],
                                main_menu_btn['position'],
                                main_menu_btn['color'],
                                main_menu_btn['text'],
                                main_menu_btn['text_size'])
        
        game_over_surf = {
            'size': (SCREEN_WIDTH, SCREEN_HEIGHT // 2 + 100),
            'position': (SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 2 + 100) // 2),
            'color': RED
        }
        self.game_over_screen.make_surface(game_over_surf['size'],
                                           game_over_surf['position'],
                                           game_over_surf['color'])
        
        game_over_text = {
            'text': 'GAME OVER!',
            'size': 90,
        }
        self.game_over_screen.make_text(game_over_text['text'],
                                        game_over_text['size'],
                                        game_over_surf['position'],
                                        antiallias=True)
        
        
        width, height = SCREEN_WIDTH, SCREEN_HEIGHT - game_over_surf['size'][1]
        main_menu_btn = {
            'id': 'm',
            'size': (width, height),
            'position': (width // 2, game_over_surf['size'][1] + height // 2),
            'color': PINK,
            'text': 'MAIN MENU',
            'text_size': 70,
        }
        self.game_over_screen.make_button(main_menu_btn['id'],
                                main_menu_btn['size'],
                                main_menu_btn['position'],
                                main_menu_btn['color'],
                                main_menu_btn['text'],
                                main_menu_btn['text_size'])
        
        
        healer_path = get_path('images', 'screens', 'start', 'healer', 'idle')
        self.start_screen.make_gif(healer_path, 200, (390, 100), loop=-1)
        
        player_path = get_path('images', 'screens', 'start', 'player', 'idle')
        self.start_screen.make_gif(player_path, 100,  (450, 112), (50, 75), loop=-1)
        
        alchemist_path = get_path('images', 'screens', 'start', 'alchemist', 'idle')
        self.start_screen.make_gif(alchemist_path, 200, (510, 100), loop=-1)
    
    def start(self):
        events = pygame.event.get()
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button != 4 and event.button != 5:
                mouse_pos = event.pos
                click_button_id = self.start_screen.button_clicked(mouse_pos)
                if click_button_id == 's':
                    self.state = 'run'
                elif click_button_id == 'e':
                    self.state = 'exit'
                    
        self.start_screen.show(self.display)
        pygame.display.update()

    def pause(self):
        events = pygame.event.get()
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button != 4 and event.button != 5:
                mouse_pos = event.pos
                click_button_id = self.pause_screen.button_clicked(mouse_pos)
                if click_button_id == 'r':
                    self.state = 'run'
                elif click_button_id == 'm':
                    self.state = 'start'

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.state = 'run'
                        
        self.pause_screen.show(self.display)
        pygame.display.update()
        pygame.mixer.music.pause()
            
        self.clock.tick(0)
        
        if self.state == 'run':
            file_path = get_path('sounds', 'sfx', 'pause', 'out')
            play_sound(file_path, 0.5)
            pygame.mixer.music.unpause()
        elif self.state == 'start':
            pygame.mixer.music.stop()
            
            file_path = get_path('sounds', 'loops', 'Thought-Soup')
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
    def game_over(self):
        events = pygame.event.get()
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button != 4 and event.button != 5:
                mouse_pos = event.pos
                click_button_id = self.game_over_screen.button_clicked(mouse_pos)
                if click_button_id == 'm':
                    self.state = 'start'
                    
        self.game_over_screen.show(self.display)
        pygame.display.update()
        
        pygame.mixer.music.stop()
        
        if self.state == 'start':
            file_path = get_path('sounds', 'loops', 'Thought-Soup')
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()

    def update_sprites(self):
        delta_t = self.clock.tick(FPS)
        ground_rect = self.ground.rect
        player_rect = self.player.rect
        
        player_pos = player_rect.center
                
        # update sprites
        keys_pressed = pygame.key.get_pressed()
        self.ground.update(keys_pressed, self.player ,delta_t)
        self.player.update(keys_pressed, ground_rect, delta_t)
        self.healer.update(ground_rect)
        self.alchemist.update(ground_rect)
        
        # bosses stuffs
        for boss in self.boss_sprites:
            if boss.health <= 0:
                self.died_bosses[boss.name] = {'position': boss.rect.center, 'timer': 800}
            
            boss.update(ground_rect, delta_t)
            if boss.shooting_cooldown == 0:
                player_close = boss.is_player_close(player_rect.center, (150, 150))
                if player_close:
                    boss.shoot(ground_rect, player_rect.center)
            
            is_player_near = boss.is_player_close(player_rect.center, boss.size)
            if is_player_near:
                self.player.collide_boss_enemy(boss.rect.center)

        revived_bosses = []
        for boss_name in self.died_bosses:
            timer = self.died_bosses[boss_name]['timer']
            boss_pos = self.died_bosses[boss_name]['position']
            self.died_bosses[boss_name]['timer'] -= 1
            
            if self.died_bosses[boss_name]['timer'] == 0:
                boss = Boss_Enemy(boss_name)
                boss.init_position(ground_rect)
                self.boss_sprites.add(boss)
                revived_bosses.append(boss_name)
                
                file_path = get_path('sounds', 'sfx', 'enemy', 'boss', 'rise_again')
                play_sound(file_path, 0.1)
        
        for revived_boss in revived_bosses:
            del self.died_bosses[revived_boss]
            
            
        # child enemies update
        for child1 in self.child1_sprites:
            child1.find_attack_aim(player_pos, self.healer)
            
            child1.update(ground_rect, delta_t)
        
        for child2 in self.child2_sprites:
            child2.find_attack_aim(player_pos, self.healer)
                
            child2.update(ground_rect, delta_t)
            
        for child1 in self.child1_sprites:
            if child1.attack_cooldown == 0:
                child1.attack(ground_rect)
        
        for child2 in self.child2_sprites:
            if child2.attack_cooldown == 0:
                child2.attack(ground_rect)
            
        self.display.fill((0, 0, 0))
        
    def handle_events(self):
        ground_rect = self.ground.rect
        
        # handle events
        events = pygame.event.get()
        for event in events:
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.state = 'pause'
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    range_x = range(0, SCREEN_WIDTH)
                    range_y = range(SCREEN_HEIGHT - 40, SCREEN_HEIGHT)
                    
                    mouse_x, mouse_y = self.mouse_pos[0], self.mouse_pos[1]
                    if (mouse_x in range_x) and (mouse_y in range_y):
                        self.player.click_on_potion(self.mouse_pos)
                    else:
                        self.player.attack(self.mouse_pos, ground_rect)
                        
                # check mouse scroll
                if event.button == 4:
                    self.player.change_weapon('scroll_up')
                elif event.button == 5:
                    self.player.change_weapon('scroll_down')
                    
            if event.type == MOUSEMOTION:
                self.mouse_pos = event.pos
                
                
        # make child_enmey1 => dirty or dusty
        if self.child1_make_timer == 0:
            number_of_child1 = len(self.child1_sprites.sprites())
            if (number_of_child1 < 6) and ('bloody' not in self.died_bosses):
                child_enemy = Child_Enemy('bloody')
                child_enemy.born(ground_rect)
                self.child1_sprites.add(child_enemy)

                self.child1_make_timer = 700
        else:
            self.child1_make_timer -= 1
                
        # make child_enemy2 => wiz
        if self.child2_make_timer == 0:
            number_of_child2 = len(self.child2_sprites.sprites())
            if (number_of_child2 < 4) and ('wiz' not in self.died_bosses):
                child_enemy = Child_Enemy('wiz')
                child_enemy.born(ground_rect)
                self.child2_sprites.add(child_enemy)
            
                self.child2_make_timer = 500
        else:
            self.child2_make_timer -= 1
            
    def show_sprites(self):
        ground_rect = self.ground.rect
        
        # show sprites
        self.ground.show(self.display)
            
        # show died bosses rising again timer
        for boss_name in self.died_bosses:
            boss_dict = {boss_name: self.died_bosses[boss_name]}
            self.show_died_boss_rising_timer(boss_dict, ground_rect)
        
        # show ground decoration: bushes and ridges
        number_of_decorations = len(self.ground.decoration_init_positions)
        for i in range(number_of_decorations):
            for j in range(len(self.ground.decoration_surfs[i])):
                ground = self.ground
                decoration_surf = ground.decoration_surfs[i][j]
                decoration_rect = ground.decoration_rects[i][j]
                self.display.blit(decoration_surf, decoration_rect)
        
        # show child enemies' born places :D
        number_of_born_places = len(self.ground.enemy_born_place_surfs)
        for i in range(number_of_born_places):
            surface = self.ground.enemy_born_place_surfs[i]
            rect = self.ground.enemy_born_place_rects[i]
            self.display.blit(surface, rect)
            
        for boss in self.boss_sprites:            
            boss.show(self.display)
        
        # show child enemies
        for child1 in self.child1_sprites:
            child1.show(self.display)
        
        for child2 in self.child2_sprites:
            child2.show(self.display)
            
        # show player, healer, alchemist and their stuffs
        self.player.show(self.mouse_pos, self.display)
        self.alchemist.show(self.display)
        self.healer.show(self.display)
        
        # show trees
        number_of_trees = len(self.ground.tree_init_positions)
        for i in range(number_of_trees):
            for j in range(len(self.ground.tree_surfs[i])):
                tree_surf = self.ground.tree_surfs[i][j]
                tree_rect = self.ground.tree_rects[i][j]
                self.display.blit(tree_surf, tree_rect)

        self.show_bottom_bar()
        
        if len(self.player.used_potions) != 0:
            self.player.show_potion_timer(self.display)
    
    def detect_collisions(self):
        player_rect = self.player.rect
        healer_rect = self.healer.rect
        
        # collision detectons
        for boss in self.boss_sprites:
            for shot in self.player.shots:
                if pygame.sprite.collide_rect(shot, boss) == True:
                    damage = self.player.weapon_damage
                    boss.shot_collide(damage)
                    shot.kill()

        for child1 in self.child1_sprites:
            if child1.state != 'born':
                # check collision between sword and child1 enemy
                if self.player.current_weapon == 0 and self.player.weapon_state == 'attack':
                    sword_rect = self.player.weapon_rect
                    if child1.rect.colliderect(sword_rect) == True:
                        damage = self.player.weapon_damage
                        child1.player_weapon_collide(damage)

                # check collision between staff fireball and child1 enemy
                elif self.player.current_weapon == 1:
                    for shot in self.player.shots:
                        if pygame.sprite.collide_rect(shot, child1) == True:
                            damage = self.player.weapon_damage
                            child1.player_weapon_collide(damage)
                            shot.kill()
        
        for child2 in self.child2_sprites:
            if child2.state != 'born':
                # check collision between sword and child2 enemy
                if self.player.current_weapon == 0 and self.player.weapon_state == 'attack':
                    sword_rect = self.player.weapon_rect
                    if child2.rect.colliderect(sword_rect) == True:
                        damage = self.player.weapon_damage
                        child2.player_weapon_collide(damage)

                    # check collision between sword and child2 shots
                    for shot in child2.shots:
                        if shot.rect.colliderect(sword_rect) == True:
                            shot.kill()

                # check collision between staff fireball and child2 enemy
                elif self.player.current_weapon == 1:
                    for shot in self.player.shots:
                        if pygame.sprite.collide_rect(shot, child2) == True:
                            damage = self.player.weapon_damage
                            child2.player_weapon_collide(damage)
                            shot.kill()
                        
                        
        for child1 in self.child1_sprites:
            if child1.state == 'attack':
                if child1.attack_aim == 'player':
                    offset = 30
                    aim_pos = player_rect.center
                elif child1.attack_aim == 'healer':
                    offset = 50
                    aim_pos = healer_rect.center

                is_enemy_near_player = child1.is_position_in_range(aim_pos, offset)

                if is_enemy_near_player == True and child1.damage_cooldown == 0:
                    if child1.attack_aim == 'player':
                        self.player.collide_enemy(child1.name)
                    elif child1.attack_aim == 'healer':
                        self.healer.collide_enemy(child1.name)

                    child1.attack_cooldown = child1.first_attack_cooldown
                    child1.damage_cooldown = 20
        
        for child2 in self.child2_sprites:
            if child2.attack_aim == 'player':
                collision_sprite = self.player
            elif child2.attack_aim == 'healer':
                collision_sprite = self.healer
                
            for shot in child2.shots:
                if pygame.sprite.collide_rect(shot, collision_sprite):
                    collision_sprite.collide_enemy(child2.name)
                    shot.kill()
                
        for boss in self.boss_sprites:
            for shot in boss.shots:
                if pygame.sprite.collide_rect(shot, self.player) == True:
                    self.player.collide_enemy('boss')
                    shot.kill()
                    
        if player_rect.colliderect(self.alchemist.potion_rect):
            if len(self.player.potions) < 3 and self.alchemist.potion != '':
                self.player.pickup_potion(self.alchemist)
            
        for swamp_rect in self.ground.swamp_rects:
            player_foot = (self.player.rect.center[0], self.player.rect.bottom)
            if swamp_rect.collidepoint((player_foot)) == True:
                self.player.collide_swamp = True
        
        teleport_name = self.ground.is_player_collide_teleport_place(player_foot)
        if teleport_name != None:
            if teleport_name == 'healer':
                npc_pos = healer_rect.center
            elif teleport_name == 'alchemist':
                alchemist_rect = self.alchemist.rect
                npc_pos = alchemist_rect.center
            
            self.player.collide_teleport_place(teleport_name, npc_pos)
        
        for void_rect in self.ground.void_rects:
            if self.player.rect.colliderect(void_rect) == True:
                self.player.kill()
                self.state = 'game-over'
            
        pygame.display.flip()
            
        if self.player.health <= 0:
            self.state = 'game-over'

        # play pause sound
        if self.state == 'pause':
            file_path = get_path('sounds', 'sfx', 'pause', 'in')
            play_sound(file_path, 0.5)
        # play game-over sound
        elif self.state == 'game-over':
            file_path = get_path('sounds', 'sfx', 'game_over_sound')
            play_sound(file_path, 0.1, 0)
        
    def loop(self):
        ground_rect = self.ground.rect
        player_rect = self.player.rect
        healer_rect = self.healer.rect
        
        player_pos = player_rect.center
        healer_pos = healer_rect.center
        
        self.update_sprites()
        self.handle_events()
        self.show_sprites()
        
        # heal player when is in healing range and check if healer can heal him because of some reasons
        player_health = self.player.health
        is_healer_should_heal = self.healer.is_healer_should_heal(player_pos, player_health)
        if is_healer_should_heal == True:
            self.healer.heal(self.player)
        
        self.detect_collisions()
        
    def show_bottom_bar(self):
        bottom_bar_surf = pygame.Surface((SCREEN_WIDTH, 40))
        bottom_bar_rect = bottom_bar_surf.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        bottom_bar_surf.fill((198, 201, 189))
        bottom_bar_surf.set_alpha(100)
        
        self.display.blit(bottom_bar_surf, bottom_bar_rect)
        
        self.player.show_health(self.display)
        self.player.show_weapon_bar(self.display)
        self.player.show_potion_bar(self.display)
        
    def show_died_boss_rising_timer(self, boss_dict, ground_rect):
        # boss_dict = ('name', {'position': tuple, 'timer': int})
        boss_dict = boss_dict.popitem()
        boss_name = boss_dict[0]
        boss_position = boss_dict[1]['position']
        boss_timer = boss_dict[1]['timer']
        
        image_num = boss_timer // 80
        image_path = get_path('images', 'enemy', 'boss', 'health_bar', str(image_num))
        timer_image = pygame.image.load(image_path)
        
        if boss_name == 'bloody':
            timer_center_pos = (ground_rect.right - 258, ground_rect.top + 100)
        elif boss_name == 'wiz':
            timer_center_pos = (ground_rect.left + 125, ground_rect.top + 270)
        timer_rect = timer_image.get_rect(center = timer_center_pos)
        
        self.display.blit(timer_image, timer_rect)
        