import pygame
import math
from random import choice
from os import path

from data.sources.shot import Shot
from data.sources.pygameGIF import GIF
from data.sources.files import Files

play_sound = Files.play_sound
get_path = Files.get_full_path

# constants
SCREEN_HEIGHT, SCREEN_WIDTH = 500, 900
GROUND_HEIGHT, GROUND_WIDTH = 563, 1000


class Player(pygame.sprite.Sprite):
    
    def __init__(self):
        super().__init__()
        self.health = 10
        
        image_path = path.join(get_path('images', 'player', 'movement', 'down', 'idle'), '1.png')
        self.image = pygame.image.load(image_path).convert_alpha()
        image_size = (35, 50)
        self.surface = pygame.transform.smoothscale(self.image, image_size)
        WHITE = (255, 255, 255)
        self.surface.set_colorkey(WHITE)
        
        self.position = [630, 370]
        self.rect = self.surface.get_rect(center = tuple(self.position))
        
        self.direction = 'down'
        self.state = 'idle'
        self.gifs = {}
        self.set_gifs()
                        
        self.shooting_power = 9
        self.shots = pygame.sprite.Group()
        
        self.collide_enemy_timer = 0
        self.is_collided_with_enemy = False
        self.collide_enemy_steps = []
        
        self.current_weapon = 1
        self.weapon_rotate_angle = 0
        self.weapon_start_angle = 0
        self.weapon_end_angle = 0
        self.weapon_angle_step = 0
        self.weapon_damage = 1
        self.weapon_state = 'normal'
        self.weapon_head_pos = []
        self.weapons = ['sword', 'staff']
        
        self.change_weapon('scroll_down')
        
        self.collide_swamp = False
        
        self.is_healing = False
        self.lowhealth_alarm_cooldown = 100
        
        self.potions = []
        self.potions_position = []
        self.used_potions = []
        self.used_potions_timer = []
        
        self.after_teleport_cooldown = 100
        self.teleported = False
        self.teleport_place = ''
        
    def set_gifs(self):
        parent_values = ['down', 'up', 'right', 'left']
        for i in range(4):
            child_values = ['run', 'idle']
            for j in range(2):
                folder_path = get_path('images', 'player', 'movement', parent_values[i], child_values[j])
                image_size = (35, 50)
                gif = GIF(folder_path, 10, image_size)
                dict_key = parent_values[i] + '_' + child_values[j]
                self.gifs[dict_key] = gif
        
    def show(self, mouse_pos, display):
        if self.direction == 'up' or self.direction == 'left' or self.direction == 'right':
            # show player shots
            if self.current_weapon == 1:
                self.show_staff_shots(display)
                
            display.blit(self.weapon_surface, self.weapon_rect)
            display.blit(self.surface, self.rect)
        else:
            display.blit(self.surface, self.rect)
            display.blit(self.weapon_surface, self.weapon_rect)
            # show player shots
            if self.current_weapon == 1:
                self.show_staff_shots(display)
                
        # show shooting power
        if self.current_weapon == 1:
            self.show_shooting_power(mouse_pos, display)
    
    def show_staff_shots(self, display):
        for shot in self.shots:
            display.blit(shot.surface, shot.rect)
    
    def show_weapon_bar(self, display):
        weapon_back_size = (40, 40)
        weapon_back_surf = pygame.Surface(weapon_back_size)
        weapon_back_surf.set_alpha(100)
        
        sword_image_path = get_path('images', 'player', 'weapons', 'sword')
        
        sword_surf = pygame.image.load(sword_image_path)
        sword_rect = sword_surf.get_rect(center = (SCREEN_WIDTH - 195, SCREEN_HEIGHT - 15))
        
        staff_image_path = get_path('images', 'player', 'weapons', 'staff')
        staff_surf = pygame.image.load(staff_image_path)
        staff_rect = staff_surf.get_rect(center = (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 20))
        
        if self.current_weapon == 0:
            weapon_back_center = (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 20)
            weapon_back_rect = weapon_back_surf.get_rect(center = weapon_back_center)
        else:
            weapon_back_center = (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 20)
            weapon_back_rect = weapon_back_surf.get_rect(center = weapon_back_center)
        
        WHITE = (255, 255, 255)
        pygame.draw.rect(weapon_back_surf, (255, 255, 255), (0, 0, 40, 40), 5)
        
        surfaces = [weapon_back_surf, sword_surf, staff_surf]
        rects = [weapon_back_rect, sword_rect, staff_rect]
        
        for i in range(3):
            display.blit(surfaces[i], rects[i])
            
    def show_potion_bar(self, display):
        center_x, center_y = 150, SCREEN_HEIGHT - 20
        for i in range(3):
            size = (40, 40)
            surface = pygame.Surface(size)
            BLACK = (0, 0, 0)
            surface.fill(BLACK)
            
            WHITE = (255, 255, 255)
            pygame.draw.rect(surface, WHITE, (0, 0, 40, 40), 5)
            surface.set_alpha(120)
            
            center_pos = (center_x, center_y)
            rect = surface.get_rect(center = center_pos)
            center_x += 50
            
            display.blit(surface, rect)
        
        center_x, center_y = 150, SCREEN_HEIGHT - 23
        for i in range(len(self.potions)):
            potion = self.potions[i]
            if potion == 'strength':
                image_path = path.join(get_path('images', 'potions', 'strength', 'idle'), '1.png')
            elif potion == 'regeneration':
                image_path = path.join(get_path('images', 'potions', 'regeneration', 'idle'), '1.png')
            elif potion == 'imortality':
                image_path = path.join(get_path('images', 'potions', 'imortality', 'idle'), '1.png')
            
            image = pygame.image.load(image_path)
            surface = pygame.transform.scale(image, (20, 35))
            
            center_pos = (center_x, center_y)
            rect = surface.get_rect(center = center_pos)
            
            if center_pos in self.potions_position:
                self.potions_position[i] = center_pos
            else:
                self.potions_position.append(center_pos)
            
            center_x += 50
            
            display.blit(surface, rect)
    
    def show_shooting_power(self, mouse_pos, display):
        shooting_power_num = self.shooting_power // 8
        
        image_path = get_path('images', 'player', 'shoot_bar', str(shooting_power_num))
        shooting_power_surf = pygame.image.load(image_path)
        
        player_pos = self.rect.center
        edge_x = mouse_pos[0] - player_pos[0]
        edge_y = mouse_pos[1] - player_pos[1]
        
        angle = math.atan2(-edge_y, edge_x)
        
        shooting_power_surf = pygame.transform.rotate(shooting_power_surf, math.degrees(angle))
        shooting_power_surf.set_alpha(200)
            
        shooting_power_rect = shooting_power_surf.get_rect(center = self.weapon_head)
        
        display.blit(shooting_power_surf, shooting_power_rect)    
            
    def show_potion_timer(self, display):
        center_x, center_y = 30, 30
        for i in range(len(self.used_potions)):
            image_num = self.used_potions_timer[i] // 40
            image_path = get_path('images', 'potions', self.used_potions[i], 'timer_bar', str(image_num))
            
            image = pygame.image.load(image_path)
            center_pos = (center_x, center_y)
            rect = image.get_rect(center = center_pos)
            center_y += 45
            
            display.blit(image, rect)
        
    def update(self, keys, ground_rect, delta_t):
        self.update_position(keys, ground_rect, delta_t)
        
        # change surface image for make it like a gif
        self.update_surface()
        
        # update shots positions
        for shot in self.shots:
            shot.update(ground_rect, delta_t)

        self.update_weapon()
        
        if len(self.used_potions) != 0:
            self.update_used_potions_timer()
            
        if self.collide_enemy_timer <= 0:
            self.is_collided_with_enemy = False
            
        if self.health < 2:
            if self.lowhealth_alarm_cooldown != 0:
                self.lowhealth_alarm_cooldown -= 1
            else:
                # play lowhealth alarm
                file_path = get_path('sounds', 'sfx', 'player', 'lowhealth_alarm')
                play_sound(file_path, 0.4)
                
                self.lowhealth_alarm_cooldown = 100
                
        self.update_shooting_power()
                
    def update_shooting_power(self):
        if self.current_weapon == 1:
            if self.shooting_power < 80:
                self.shooting_power += 1
                
    def update_position(self, keys_pressed, ground_rect, delta_t):
        changing_value = 0.09
        
        if self.collide_swamp == True:
            changing_value = 0.02
            
        if self.teleported == True:
            changing_value = 0
        
        if self.is_collided_with_enemy == False:
            top_or_left_limit = 0.09 * delta_t
            previous_direction = self.direction

            if keys_pressed[pygame.K_w] == True and self.rect.top > top_or_left_limit:
                self.position[1] += -(changing_value * delta_t)
                self.direction = 'up'
                self.state = 'run'
            elif keys_pressed[pygame.K_s] == True and self.rect.bottom < SCREEN_HEIGHT :
                self.position[1] += (changing_value * delta_t)
                self.direction = 'down'
                self.state = 'run'
            elif keys_pressed[pygame.K_a] == True and self.rect.left > top_or_left_limit:
                self.position[0] += -(changing_value * delta_t)
                self.direction = 'left'
                self.state = 'run'
            elif keys_pressed[pygame.K_d] == True and self.rect.right < SCREEN_WIDTH:
                self.position[0] += (changing_value * delta_t)
                self.direction = 'right'
                self.state = 'run'
            else:
                self.state = 'idle'

            if previous_direction != self.direction:
                self.weapon_state = 'normal'

        else:
            changing_x = (self.collide_enemy_steps[0] * delta_t)
            changing_y = (self.collide_enemy_steps[1] * delta_t)
            if self.rect.left > changing_x and self.rect.right < SCREEN_WIDTH:
                self.position[0] += (self.collide_enemy_steps[0] * delta_t)
            if self.rect.top > changing_y and self.rect.bottom < SCREEN_HEIGHT:
                self.position[1] += (self.collide_enemy_steps[1] * delta_t)
            self.collide_enemy_timer -= 1
            
            
        if self.teleported == True:
            self.state = 'idle'
            if self.after_teleport_cooldown != 0:
                self.after_teleport_cooldown -= 1
            else:
                self.teleported = False

        self.rect.center = (int(self.position[0]), int(self.position[1]))
        self.collide_swamp = False
        
    def update_used_potions_timer(self):
        timer_zero_potion_indexes = []
        for i in range(len(self.used_potions)):
            self.used_potions_timer[i] -= 1
            if self.used_potions_timer[i] == 0:
                timer_zero_potion_indexes.append(i)
        
        for index in timer_zero_potion_indexes:
            del self.used_potions[index]
            del self.used_potions_timer[index]
        
    def update_surface(self):
        gif_key = self.direction + "_" + self.state
        current_gif = self.gifs[gif_key]
        self.surface = current_gif.render_surface()
        BLACK = (0, 0, 0)
        self.surface.set_colorkey(BLACK)
    
    def shoot(self, mouse_pos, ground_rect):
        if self.direction == 'up' or self.direction == 'right':
            shot_pos = (self.weapon_rect.right, self.weapon_rect.top)
        elif self.direction == 'down' or self.direction == 'left':
            shot_pos = (self.weapon_rect.left, self.weapon_rect.top)
        
        time = self.shooting_power // 8 * 2
        speed = 0.3
        shot = Shot(self.weapon_head , ground_rect, time, speed)
        
        fireball_image_path = get_path('images', 'player', 'fireball')
        shot.change_image(fireball_image_path)
        
        player_pos = self.rect.center
        edge_x = mouse_pos[0] - player_pos[0]
        edge_y = mouse_pos[1] - player_pos[1]

        try:
            angle = abs(math.atan(edge_y / edge_x))
        except ZeroDivisionError:
            angle = math.radians(90)
            
        shot.set_coord_steps(angle, edge_x, edge_y)
        self.shots.add(shot)
    
    def collide_boss_enemy(self, enemy_pos):
        if 'imortality' not in self.used_potions:
            self.health -= 2
            
            file_path = get_path('sounds', 'sfx', 'player', 'got_hit')
            play_sound(file_path, 0.4)
            
        player_pos = self.rect.center
        
        edge_x = player_pos[0] - enemy_pos[0]
        edge_y = player_pos[1] - enemy_pos[1]
        
        try:
            angle = math.atan(abs(edge_y / edge_x))
        except ZeroDivisionError:
            angle = math.radians(90)
        
        x_step = 1 * math.cos(angle)
        x_step *= -1 if edge_x < 0 else 1
        
        y_step = 1 * math.sin(angle)
        y_step *= -1 if edge_y < 0 else 1
        
        self.collide_enemy_steps = [x_step, y_step]
        self.is_collided_with_enemy = True
        self.collide_enemy_timer = 6
    
    def collide_enemy(self, enemy_name):
        if 'imortality' not in self.used_potions:
            if enemy_name == 'boss':
                self.health -= 1
            elif enemy_name == 'dusty' or enemy_name == 'dirty':
                self.health -= 1
            elif enemy_name == 'wiz':
                self.health -= 0.5

            file_path = get_path('sounds', 'sfx', 'player', 'got_hit')
            play_sound(file_path, 0.2)
        
    def show_health(self, display):
        if self.health < 0:
            self.health = 0
        
        health_back_surface = pygame.Surface((250, 40))
        WHITE = (255, 255, 255)
        pygame.draw.rect(health_back_surface, WHITE, (0, 0, 250, 40), 5)
        health_back_surface.set_alpha(100)
        
        health_surface_size = (250, 40)
        health_surface = pygame.Surface(health_surface_size)
        BLACK = (0, 0, 0)
        health_surface.set_colorkey(BLACK)
        
        half_heart = False
        if int(self.health) < self.health:
            half_heart = True
            
        full_hearths = int(self.health)

        left_offset, top_offset = 10, 12
        width, height = 24, 20
        heart_size = (width, height)
        for i in range(full_hearths):
            image_path = get_path('images', 'player', 'health', 'heart')
            heart_image = pygame.image.load(image_path)
            health_surface.blit(heart_image, ((left_offset, top_offset), heart_size))
            left_offset += 23
        
        empty_hearts = 10 - full_hearths
        if half_heart == True:
            image_path = get_path('images', 'player', 'health', 'half_heart')
            half_heart_image = pygame.image.load(image_path)
            health_surface.blit(half_heart_image, ((left_offset, top_offset), heart_size))
            left_offset += 23
            
            empty_hearts -= 1
            
        for i in range(empty_hearts):
            image_path = get_path('images', 'player', 'health', 'empty_heart')
            empty_heart_image = pygame.image.load(image_path)
            health_surface.blit(empty_heart_image, ((left_offset, top_offset), heart_size))
            left_offset += 23
            
        health_rect = health_surface.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        
        display.blit(health_back_surface, health_rect)
        display.blit(health_surface, health_rect)
        
    def change_weapon(self, scrolling_type):
        change_image = False
        if scrolling_type == 'scroll_up' and self.current_weapon == 0:
            self.current_weapon = 1
            change_image = True
        elif scrolling_type == 'scroll_down' and self.current_weapon == 1:
            self.current_weapon = 0
            change_image = True
        
        self.weapon_state = 'normal'
        if change_image == True:
            curr_weapon_name = self.weapons[self.current_weapon]
            image_path = get_path('images', 'player', 'weapons', curr_weapon_name)
            self.weapon_image = pygame.image.load(image_path).convert_alpha()
            self.weapon_rect = self.weapon_image.get_rect(center = self.rect.center)
            
        if self.current_weapon == 0:
            self.shooting_power = 0
        
    def update_weapon(self):
        self.update_weapon_surface()
        
        # update weapon damage, if strength potion was used, weapon damage should increase
        self.update_weapon_damage()
            
        self.update_weapon_head_pos()
        
    def update_weapon_damage(self):
        sword_damage = 0.08
        staff_damage = 1
        if 'strength' in self.used_potions:
            if self.current_weapon == 0:
                sword_damage = 0.2
            else:
                staff_damage = 2
        
        if self.current_weapon == 0:
            self.weapon_damage = sword_damage
        else:
            self.weapon_damage = staff_damage
        
    def update_weapon_head_pos(self):
        if self.direction == 'up':
            weapon_center_x = self.weapon_rect.center[0] + 9
            weapon_center_y = self.weapon_rect.top + 7
        elif self.direction == 'down':
            weapon_center_x = self.weapon_rect.left + 9
            weapon_center_y = self.weapon_rect.top + 6
        elif self.direction == 'right':
            weapon_center_x = self.weapon_rect.right - 5
            weapon_center_y = self.weapon_rect.top + 5
        elif self.direction == 'left':
            weapon_center_x = self.weapon_rect.left + 5
            weapon_center_y = self.weapon_rect.top + 5
            
        self.weapon_head = (weapon_center_x, weapon_center_y)
        
    def update_weapon_surface(self):
        player_x = self.rect.center[0]
        player_y = self.rect.center[1]

        # update weapon surface(rotate or flip)
        if self.direction == 'up':
            self.weapon_surface = pygame.transform.rotate(self.weapon_image, -65)
        elif self.direction == 'down':
            self.weapon_surface = pygame.transform.rotate(self.weapon_image, -10)
        elif self.direction == 'left':
            self.weapon_surface = self.weapon_image
        elif self.direction == 'right':
            self.weapon_surface = pygame.transform.flip(self.weapon_image, True, False)

        if self.weapon_state == 'attack':
            self.weapon_surface = pygame.transform.rotate(self.weapon_surface, self.weapon_rotate_angle)

            if abs(self.weapon_rotate_angle) <= abs(self.weapon_end_angle):
                if self.weapon_rotate_angle == self.weapon_end_angle:
                    self.weapon_angle_step *= -1
                    
                self.weapon_rotate_angle += self.weapon_angle_step
                
                if abs(self.weapon_rotate_angle) <= 0:
                    self.weapon_state = 'normal'
                    
        # update weapon rect
        if self.direction == 'up':
            offset_x, offset_y = 5, -5
            if self.current_weapon == 1:
                offset_x += 5
        elif self.direction == 'down':
            offset_x, offset_y = -15, 5
        elif self.direction == 'left':
            offset_x, offset_y = -10, 5
            if self.current_weapon == 1:
                offset_x += -5
        elif self.direction == 'right':
            offset_x, offset_y = 10, 5
            if self.current_weapon == 1:
                offset_x += 5
        
        self.weapon_rect.center = (player_x + offset_x, player_y + offset_y)    
            
    def attack(self, mouse_pos, ground_rect):
        if self.current_weapon == 0:
            if self.direction == 'up':
                end_rotate_angle = -28
                angle_step = -7
            elif self.direction == 'down':
                end_rotate_angle = 28
                angle_step = 7
            elif self.direction == 'left':
                end_rotate_angle = 49
                angle_step = 7
            elif self.direction == 'right':
                end_rotate_angle = -35
                angle_step = -7
            self.weapon_rotate_angle = 0
            self.weapon_end_angle = end_rotate_angle
            self.weapon_angle_step = angle_step
            self.weapon_state = 'attack'
            
            sound_file_path = get_path('sounds', 'sfx', 'player', 'sword')
            
        elif self.current_weapon == 1:
            self.shoot(mouse_pos, ground_rect)
            self.shooting_power = 9
            
            sound_file_path = get_path('sounds', 'sfx', 'player', 'shoot')
            
        play_sound(sound_file_path, 0.1)
           
    def pickup_potion(self, alchemist):
        potion_name = alchemist.potion
        self.potions.append(potion_name)
        alchemist.potion = ''
        alchemist.give_potion_cooldown = 1000   
        
        sound_file_path = get_path('sounds', 'sfx', 'player', 'pickup_potion')
        play_sound(sound_file_path, 0.2)
     
    def click_on_potion(self, mouse_pos):
        clicked_potion = ''
        size = len(self.potions)
        for i in range(size):
            potion_pos = self.potions_position[i]
            
            range_x = range(potion_pos[0] - 20, potion_pos[0] + 20)
            range_y = range(potion_pos[1] - 20, potion_pos[1] + 20)
            
            mouse_x = mouse_pos[0]
            mouse_y = mouse_pos[1]
            if (mouse_x in range_x) and (mouse_y in range_y):
                clicked_potion = self.potions[i]
                potion_index = i
                break
        
        if clicked_potion == '':
            return
        
        if clicked_potion not in self.used_potions:
            if clicked_potion != 'regeneration':
                self.used_potions.append(clicked_potion)
                self.used_potions_timer.append(400)
                
                self.potions.pop(potion_index)
                self.potions_position.pop(potion_index)
            else:
                if self.health < 10:
                    self.health = 10
                    self.potions.pop(potion_index)
                    self.potions_position.pop(potion_index)
                    
            if clicked_potion == 'imortality':
                file_path = get_path('sounds', 'sfx', 'player', 'use_imortality')
            elif clicked_potion == 'strength':
                file_path = get_path('sounds', 'sfx', 'player', 'use_strength')
            elif clicked_potion == 'regeneration':
                file_path = get_path('sounds', 'sfx', 'player', 'use_regeneration')
                
            play_sound(file_path, 0.2)
            
    def collide_teleport_place(self, teleport_place_name, npc_pos):
        if teleport_place_name == 'healer':
            telport_pos = [npc_pos[0] - 100, npc_pos[1] + 15]
        elif teleport_place_name == 'alchemist':
            telport_pos = [npc_pos[0] + 60, npc_pos[1] + 15]
            
        self.position = telport_pos
        self.after_teleport_cooldown = 100
        self.teleported = True
        self.teleport_place = teleport_place_name
        
        file_path = get_path('sounds', 'sfx', 'teleport_sound')
        play_sound(file_path, 0.2)