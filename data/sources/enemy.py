import pygame
import math
from random import choice
from os import path

from data.sources.shot import Shot
from data.sources.pygameGIF import GIF
from data.sources.files import Files

play_sound = Files.play_sound
get_path = Files.get_full_path

class Child_Enemy(pygame.sprite.Sprite):
    
    def __init__(self, father_name):
        super().__init__()
        
        if father_name == 'bloody':
            names = ['dusty', 'dirty']
            self.name = choice(names)
        elif father_name == 'wiz':
            self.name = 'wizzy'
        
        folder_path = get_path('images', 'enemy', 'child', self.name, 'state', 'idle')
        if father_name == 'bloody':
            attack_cooldown = 30
            speed = 0.02
            player_offset = 50
            health = 3
        elif father_name == 'wiz':
            attack_cooldown = 100
            speed = 0.04
            player_offset = 120
            self.shots = pygame.sprite.Group()
            health = 5
            
        self.gif = GIF(folder_path, 10)
        
        self.damage_cooldown = 50
        self.speed = speed
        self.first_attack_cooldown = attack_cooldown
        self.attack_cooldown = attack_cooldown
        self.player_offset = player_offset
        self.health = health
        self.state = 'born'
        
        self.attack_aim = 'player'
        self.attack_aim_pos = ()
        
        self.moving_steps = []
        self.attack_moving_steps = []
    
    def born(self, ground_rect):
        folder_path = get_path('images', 'enemy', 'child', self.name, 'state', 'born')
        if self.name == 'dirty':
            self.start_pos = (530, 170)
        elif self.name == 'dusty':
            self.start_pos = (915, 230)
        elif self.name == 'wizzy':
            self.start_pos = (285, 330)
        
        self.born_gif = GIF(folder_path, 50, loop=1)
        
        born_surface = self.born_gif.render_surface()
        self.surface = born_surface
        
        init_x = ground_rect.left + self.start_pos[0]
        init_y = ground_rect.top + self.start_pos[1]
        center_pos = (init_x, init_y)
        
        born_rect = born_surface.get_rect(center = center_pos)
        self.rect = born_rect
        
        self.changing_pos = [self.start_pos[0], self.start_pos[1]]
        
    def show(self, display):
        display.blit(self.surface, self.rect)
        
        if self.state != 'born':
            self.show_health(display)
        
        if self.name == 'wizzy':
            for shot in self.shots:
                display.blit(shot.surface, shot.rect)
                
    def show_health(self, display):
        health_num = int(self.health)
        image_path = get_path('images', 'enemy', 'child', self.name, 'health_bar', str(health_num))
        health_surface = pygame.image.load(image_path)
        
        enemy_center_x = self.rect.center[0]
        enemy_top = self.rect.top
        health_rect = health_surface.get_rect(center = (enemy_center_x, enemy_top - 7))
        
        display.blit(health_surface, health_rect)
    
    def update(self, ground_rect, delta_t):
        if self.state == 'born':
            born_surface = self.born_gif.render_surface()
            self.surface = born_surface
            
            center_x = ground_rect.left + self.start_pos[0]
            center_y = ground_rect.top + self.start_pos[1]
            self.rect.center = (int(center_x), int(center_y))
            
            if self.born_gif.current_loop == 1:
                self.state = 'walk'
                
        elif self.state == 'walk':
            position_in_range = self.is_position_in_range(self.attack_aim_pos, self.player_offset)
            if position_in_range == True:
                self.moving_steps = (0, 0)
                if self.attack_cooldown > 0:
                    self.attack_cooldown -= 1
            else:
                self.moving_steps = self.find_moving_steps(self.attack_aim_pos, self.speed)
                
            self.surface = self.gif.render_surface()
            
            self.changing_pos[0] += (self.moving_steps[0] * delta_t)
            self.changing_pos[1] += (self.moving_steps[1] * delta_t)
            
            center_x = ground_rect.left + self.changing_pos[0]
            center_y = ground_rect.top + self.changing_pos[1]
            
            self.rect.center = (int(center_x), int(center_y))
                
        elif self.state == 'attack':
            if self.name == 'dirty' or self.name == 'dusty':
                self.surface = self.gif.render_surface()
                
                self.changing_pos[0] += (self.attack_moving_steps[0] * delta_t)
                self.changing_pos[1] += (self.attack_moving_steps[1] * delta_t)
                
                center_x = ground_rect.left + self.changing_pos[0]
                center_y = ground_rect.top + self.changing_pos[1]
                
                self.rect.center = (int(center_x), int(center_y))
                    
                if self.attack_aim == 'player':
                    offset = (30, 45)
                elif self.attack_aim == 'healer':
                    offset = (55, 105)
                
                is_in_range = self.is_position_in_range(self.attack_aim_pos, 20)
                if is_in_range == True:
                    self.attack_moving_steps[0] *= -1
                    self.attack_moving_steps[1] *= -1
                    
            position_in_range = self.is_position_in_range(self.attack_aim_pos, self.player_offset)
            if position_in_range == False:
                self.state = 'walk'
                self.attack_cooldown = self.first_attack_cooldown
                
        # update shots position
        if self.name == 'wizzy':
            for shot in self.shots:
                shot.update(ground_rect, delta_t)
                
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
        
        if self.health < 1:
            self.kill()
        
    def is_position_in_range(self, base_pos, offset):
        if type(offset) != tuple:
            offset = (offset, offset)
        destination_range_x1 = base_pos[0] - offset[0]
        destination_range_x2 = base_pos[0] + offset[0]
        
        destination_range_y1 = base_pos[1] - offset[1]
        destination_range_y2 = base_pos[1] + offset[1]
        
        destination_ranges = (range(destination_range_x1, destination_range_x2), range(destination_range_y1, destination_range_y2))

        center_x = self.rect.center[0]
        center_y = self.rect.center[1]
        
        if (center_x in destination_ranges[0]) and (center_y in destination_ranges[1]):
            return True
        else:
            return False
        
    def find_attack_aim(self, player_pos, healer):
        center_pos = self.rect.center
        healer_pos = healer.rect.center
        
        player_distance_x = center_pos[0] - player_pos[0]
        player_distance_y = center_pos[1] - player_pos[1]
        player_distance = math.sqrt(player_distance_x**2 + player_distance_y**2)
        
        healer_distance_x = center_pos[0] - healer_pos[0]
        healer_distance_y = center_pos[1] - healer_pos[1]
        healer_distance = math.sqrt(healer_distance_x**2 + healer_distance_y**2) + 50

        previous_attack_aim = self.attack_aim
        healer_health = healer.health
        healer_is_hurted = healer.is_hurted
        
        if player_distance > healer_distance and healer_health > 0 and healer_is_hurted == False:
            self.attack_aim = 'healer'
            self.attack_aim_pos = healer.rect.center
        else:
            self.attack_aim = 'player'
            self.attack_aim_pos = player_pos
            
        if self.attack_aim != previous_attack_aim and self.state != 'born':
            self.state = 'walk'
        
    def find_moving_steps(self, attack_aim_pos, speed):
        center_x = self.rect.center[0]
        center_y = self.rect.center[1]
        
        edge_x = attack_aim_pos[0] - center_x
        edge_y = attack_aim_pos[1] - center_y
        
        try:
            angle = abs(math.atan(edge_y / edge_x))
        except ZeroDivisionError:
            angle = math.radians(90)
            
        step_x = speed * math.cos(angle)
        step_y = speed * math.sin(angle)
        
        step_x *= -1 if edge_x < 0 else 1
        step_y *= -1 if edge_y < 0 else 1
        
        moving_steps = [step_x, step_y]
        return moving_steps
    
    def attack(self, ground_rect):
        if self.name == 'dirty' or self.name == 'dusty':
            self.state = 'attack'
            self.attack_moving_steps = self.find_moving_steps(self.attack_aim_pos, 0.3)
        elif self.name == 'wizzy':
            center_pos = self.rect.center
            time, speed = 110, 0.1
            shoot = Shot(center_pos, ground_rect, time, speed)
            
            fireball_image_path = get_path('images', 'enemy', 'child', 'wizzy', 'fireball')
            shoot.change_image(fireball_image_path)
            
            center_x = self.rect.center[0]
            center_y = self.rect.center[1]
            
            edge_x = self.attack_aim_pos[0] - center_x
            edge_y = self.attack_aim_pos[1] - center_y
            
            try:
                angle = abs(math.atan(edge_y / edge_x))
            except ZeroDivisionError:
                angle = math.radians(90)
                
            shoot.set_coord_steps(angle, edge_x, edge_y)
            self.shots.add(shoot)
            
        self.attack_cooldown = self.first_attack_cooldown
        
        if self.attack_aim == 'player':
            # play attack sound
            if self.name == 'dusty' or self.name == 'dirty':
                file_path = get_path('sounds', 'sfx', 'enemy', 'child', 'dusty_dirty_attack')
            elif self.name == 'wizzy':
                file_path = get_path('sounds', 'sfx', 'enemy', 'child', 'wizzy_shoot')
                
            play_sound(file_path, 0.1)
    
    def player_weapon_collide(self, damage):
        self.health -= damage
        
class Boss_Enemy(pygame.sprite.Sprite):
    
    def __init__(self, name='bloody'):
        super().__init__()
        self.shots = pygame.sprite.Group()
        self.health = 20
        
        self.shooting_cooldown = 60
        
        self.shot_collide_timer = 0
        
        self.name = name
        if self.name == 'bloody':
            folder_path = get_path('images', 'enemy', 'boss', 'bloody', 'idle')
            self.gif = GIF(folder_path, 20, (85, 105))
        elif self.name == 'wiz':
            folder_path = get_path('images', 'enemy', 'boss', 'wiz', 'idle')
            self.gif = GIF(folder_path, 25, (60, 100))
            
        self.bound_surf = pygame.Surface((290, 290))
        self.bound_surf.set_alpha(50)
    
    def init_position(self, ground_rect):
        if self.name == 'bloody':
            pos_x = ground_rect.right - 260
            pos_y = ground_rect.top + 70
        else:
            pos_x = ground_rect.left + 125
            pos_y = ground_rect.top + 260
        
        self.surface = self.gif.render_surface()
        
        self.rect = self.surface.get_rect(center = (pos_x, pos_y))
        self.size = self.surface.get_size()
        
        self.bound_rect = self.bound_surf.get_rect(center = self.rect.center)
        
    def update(self, ground_rect, delta_t):
        if self.name == 'bloody':
            self.rect.center = (ground_rect.right - 260, ground_rect.top + 70)
        else:
            self.rect.center = (ground_rect.left + 125, ground_rect.top + 260)
        
        self.bound_rect.center = self.rect.center
        
        if self.shot_collide_timer == 0:
            self.surface = self.gif.render_surface()
        else:
            if self.shot_collide_timer <= 50 and self.health <= 20:
                self.health += 0.5
            self.shot_collide_timer -= 1
        
        for shot in self.shots:
            shot.update(ground_rect, delta_t)

        if self.shooting_cooldown > 0:
            self.shooting_cooldown -= 1
        else:
            self.shooting_cooldown = 40
        
        if self.health <= 0:
            # play death sound
            file_path = get_path('sounds', 'sfx', 'enemy', 'boss', 'boss_killed')
            play_sound(file_path, 0.3)
            self.kill()
            
    def show(self, display):
        display.blit(self.bound_surf, self.bound_rect)
        for shot in self.shots:
            display.blit(shot.surface, shot.rect)
        
        display.blit(self.surface, self.rect)
        
        if self.shot_collide_timer != 0:
            self.show_health(display)
        
    def shoot(self, ground_rect, player_pos):
        enemy_pos = self.rect.center
        edge_x = player_pos[0] - enemy_pos[0]
        edge_y = player_pos[1] - enemy_pos[1]
        
        shot = Shot(enemy_pos, ground_rect, 150, 0.1)
        
        fireball_path = get_path('images', 'enemy', 'boss', self.name, 'fireball')
        shot.change_image(fireball_path)
        
        try:
            angle = abs(math.atan(edge_y / edge_x))
        except ZeroDivisionError:
            angle = 90
        
        shot.set_coord_steps(angle, edge_x, edge_y)
        self.shots.add(shot)
        
        # play shot sound
        if self.name == 'bloody':
            file_path = get_path('sounds', 'sfx', 'enemy', 'boss', 'bloody_shoot')
        elif self.name == 'wiz':
            file_path = get_path('sounds', 'sfx', 'enemy', 'boss', 'wiz_shoot')
        play_sound(file_path, 0.1)
    
    def shot_collide(self, damage):
        if self.health > 0:
            self.health -= damage * 2
        self.shot_collide_timer = 300
        
        image_path = path.join(get_path('images', 'enemy', 'boss', self.name, 'idle'), '1.png')
        image = pygame.image.load(image_path)
        
        if self.name == 'bloody':
            new_scale = (85, 105)
        elif self.name == 'wiz':
            new_scale = (60, 100)
            
        self.surface = pygame.transform.scale(image, new_scale)
        
        file_name = get_path('sounds', 'sfx', 'enemy', 'boss', 'got_hit_with_fireball')
        play_sound(file_name, 0.5)
        
    def show_health(self, display: pygame.Surface):
        health_num = int(self.health // 2)
        health_image_path = get_path('images', 'enemy', 'boss', 'health_bar', str(health_num))
        health_image = pygame.image.load(health_image_path)
        
        enemy_center_pos = self.rect.center
        health_center_pos = (enemy_center_pos[0], self.rect.top)
        health_rect = health_image.get_rect(center = health_center_pos)
        
        display.blit(health_image, health_rect)
    
    def is_player_close(self, player_pos: tuple, range_val: tuple):
        enemy_pos = self.rect.center
        limit_x1, limit_x2 = enemy_pos[0] - range_val[0], enemy_pos[0] + range_val[0]
        limit_y1, limit_y2 = enemy_pos[1] - range_val[1], enemy_pos[1] + range_val[1]
        
        player_x, player_y = player_pos[0], player_pos[1]
        if (limit_x1 < player_x and player_x < limit_x2) and (limit_y1 < player_y and player_y < limit_y2):
            return True
        else:
            return False
    