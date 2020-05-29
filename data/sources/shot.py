import pygame
import math

class Shot(pygame.sprite.Sprite):
    
    def __init__(self, center_pos, ground_rect, time, speed):
        super().__init__()
        image = pygame.image.load(r'data\images\characters\player\fireball\1.png')
        self.surface = image
        
        self.coord_steps = [0, 0]
        self.center_pos = [center_pos[0], center_pos[1]]
        self.diff_pos = [ground_rect.right - center_pos[0], ground_rect.bottom - center_pos[1]]
        self.rect = self.surface.get_rect(center = tuple(self.center_pos))
        self.time = time
        self.speed = speed

    def change_image(self, image_path):
        self.surface = pygame.image.load(image_path)
    
    def set_coord_steps(self, angle, edge_x, edge_y):
        x_step = self.speed * math.cos(angle)
        x_step *= -1 if edge_x < 0 else 1
        
        y_step = self.speed * math.sin(angle)
        y_step *= -1 if edge_y < 0 else 1
        
        self.coord_steps = [x_step, y_step]
        
        if edge_x > 0 and edge_y < 0:
            rotation_angle = angle
        elif edge_x < 0 and edge_y < 0:
            rotation_angle = math.radians(180) - angle
        elif edge_x < 0 and edge_y > 0:
            rotation_angle = math.radians(180) + angle
        else:
            rotation_angle = math.radians(360) - angle
        self.surface = pygame.transform.rotate(self.surface, math.degrees(rotation_angle))

    def update(self, ground_rect, delta_t):
        self.diff_pos[0] -= (self.coord_steps[0] * delta_t)
        self.diff_pos[1] -= (self.coord_steps[1] * delta_t)
        
        self.center_pos[0] = ground_rect.right - self.diff_pos[0]
        self.center_pos[1] = ground_rect.bottom - self.diff_pos[1]
        
        self.rect.center = (int(self.center_pos[0]), int(self.center_pos[1]))
        
        if self.time != 0:
            self.time -= 1
        else:
            self.kill()
        
        if self.rect.bottom < ground_rect.top or self.rect.top > ground_rect.bottom or self.rect.right < ground_rect.left or self.rect.left > ground_rect.right:
            self.kill()