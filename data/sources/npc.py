import pygame
from random import choice

from data.sources.pygameGIF import GIF
from data.sources.files import Files

play_sound = Files.play_sound
get_path = Files.get_full_path

class Healer(pygame.sprite.Sprite):
    
    def __init__(self):
        super().__init__()
        
        folder_path = get_path('images', 'npc', 'healer', 'idle')
        self.gif = GIF(folder_path, 10, loop=-1)
        self.surface = self.gif.render_surface()
        self.init_position = [830, 410]
        self.rect = self.surface.get_rect(center = tuple(self.init_position))
        
        self.healing_range_surf = pygame.Surface((90, 60))
        LIGHT_YELLOW = (254, 242, 110)
        self.healing_range_surf.fill((LIGHT_YELLOW))
        self.healing_range_surf.set_alpha(50)
        self.healing_range_rect = self.healing_range_surf.get_rect(center = (0, 0))
        self.healing_cooldown = 50
        
        folder_path = get_path('images', 'npc', 'healer', 'hurted')
        self.hurted_gif = GIF(folder_path, 10, loop=-1)
        self.is_hurted = False
        
        self.health = 10
        
        self.collide_enemy_timer = 300
        
    def update(self, ground_rect):
        center_x = ground_rect.left + self.init_position[0]
        center_y = ground_rect.top + self.init_position[1]
        center_pos = (center_x, center_y)
        self.rect = self.surface.get_rect(center = center_pos)
        
        center_x = ground_rect.left + self.init_position[0] - 130
        center_y = ground_rect.top + self.init_position[1] + 40
        center_pos = (center_x, center_y)
        self.healing_range_rect.center = center_pos
        
        if self.is_hurted == False:
            self.surface = self.gif.render_surface()
        else:
            self.surface = self.hurted_gif.render_surface()
            if self.health >= 10:
                self.is_hurted = False
                self.health = 10
        
        if self.healing_cooldown != 0:
            self.healing_cooldown -= 1
            
        if self.collide_enemy_timer != 0:
            self.collide_enemy_timer -= 1
        else:
            if self.health < 10:
                self.health += 0.01
                
        if self.health <= 0:
            self.is_hurted = True
        
    def show(self, display):
        display.blit(self.healing_range_surf, self.healing_range_rect)
        display.blit(self.surface, self.rect)
        self.show_health(display)
        
    def show_health(self, display):
        if self.health < 0:
            self.health = 0
        
        health_num = int(self.health)
        image_path = get_path('images', 'npc', 'healer', 'health_bar', str(health_num))
        health_surf = pygame.image.load(image_path)
        
        center_x = self.rect.center[0]
        center_y = self.rect.top - 5
        center_pos = (center_x, center_y)
        health_rect = health_surf.get_rect(center = center_pos)
        
        display.blit(health_surf, health_rect)
        
    def is_player_in_heal_position(self, player_pos):
        treshold_x1 = self.healing_range_rect.left
        treshold_x2 = self.healing_range_rect.right
        treshold_x = range(treshold_x1, treshold_x2)
        
        treshold_y1 = self.healing_range_rect.top
        treshold_y2 = self.healing_range_rect.bottom
        treshold_y = range(treshold_y1, treshold_y2)
        
        if (player_pos[0] in treshold_x) and (player_pos[1] in treshold_y):
            return True
        else:
            return False
    
    def heal(self, player):
        player.health += 0.5
        player.is_healing = True
        self.healing_cooldown = 50
        
        file_path = get_path('sounds', 'sfx', 'player', 'heal')
        play_sound(file_path, 0.05)
        
    def collide_enemy(self, enemy_name):
        if enemy_name == 'dusty' or enemy_name == 'dirty':
            if self.health > 0:
                self.health -= 1
        elif enemy_name == 'wiz':
            if self.health >= 0.5:
                self.health -= 0.5
                
        self.collide_enemy_timer = 300
        
        file_path = get_path('sounds', 'sfx', 'npc', 'healer', 'got_hit')
        play_sound(file_path, 0.1)
        
    def is_healer_should_heal(self, player_pos, player_health):
        is_in_healing_range = self.is_player_in_heal_position(player_pos)
        if is_in_healing_range == True and self.healing_cooldown == 0 and player_health < 9.9 and self.is_hurted == False:
            return True
        else:
            return False
        
class Alchemist(pygame.sprite.Sprite):
    
    def __init__(self):
        super().__init__()
        
        folder_path = get_path('images', 'npc', 'alchemist', 'idle')
        self.gif = GIF(folder_path, 10, (40, 80), loop=-1)
        self.surface = self.gif.render_surface()
        
        self.init_position = [270, 40]
        self.rect = self.surface.get_rect(center = self.init_position)
        
        self.potion = ''
        self.potion_gif = None
        self.potion_surface = None
        self.potion_rect = None
        self.potion_init_pos = [330, 55]
        self.give_potion_cooldown = 0
    
    def show(self, display):
        display.blit(self.surface, self.rect)
        
        if self.potion != '':
            display.blit(self.potion_surface, self.potion_rect)
    
    def update(self, ground_rect):
        self.surface = self.gif.render_surface()
        
        center_x = ground_rect.left + self.init_position[0]
        center_y = ground_rect.top + self.init_position[1]
        center_pos = (center_x, center_y)
        self.rect.center = center_pos
        
        if self.give_potion_cooldown != 0 and self.potion == '':
            self.give_potion_cooldown -= 1
            
        if self.give_potion_cooldown == 0:
            if self.potion != '':
                self.potion_surface = self.potion_gif.render_surface()

                center_x = ground_rect.left + self.potion_init_pos[0]
                center_y = ground_rect.top + self.potion_init_pos[1]
                potion_center_pos = (center_x, center_y)

                self.potion_rect.center = potion_center_pos
            else:
                self.give_potion(ground_rect)
    
    def give_potion(self, ground_rect):
        potions = ['strength', 'imortality', 'regeneration']
        potion = choice(potions)
        self.potion = potion
        
        folder_path = get_path('images', 'potions', potion, 'idle')
        self.potion_gif = GIF(folder_path, 10, (20, 38), loop=-1)
        self.potion_surface = self.potion_gif.render_surface()
        self.potion_rect = self.potion_surface.get_rect(center = self.potion_init_pos)
        
        file_path = get_path('sounds', 'sfx', 'npc', 'alchemist', 'give_potion')
        play_sound(file_path, 0.4)