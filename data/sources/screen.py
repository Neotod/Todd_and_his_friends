import pygame
from data.sources.pygameGIF import GIF
from data.sources.button import Button

SCREEN_HEIGHT, SCREEN_WIDTH = 500, 900
WHITE = (255, 255, 255)

class Screen:
    
    def __init__(self, color, size=(SCREEN_WIDTH, SCREEN_HEIGHT), center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)):
        self.surface = pygame.Surface(size)
        self.surface.fill(color)
        
        self.color = color
        
        self.rect = self.surface.get_rect(center = center_pos)
        
        self.surfaces = []
        self.rects = []
        
        self.buttons = []
        
        self.gifs = []
        self.gifs_rects = []
        
    def show(self, display):
        self.surface.fill(self.color)
        
        for i in range(len(self.surfaces)):
            surface = self.surfaces[i]
            rect = self.rects[i]
            self.surface.blit(surface, rect)

        for button in self.buttons:
            button.show(self.surface)

        for i in range(len(self.gifs)):
            surface = self.gifs[i].render_surface()
            rect = self.gifs_rects[i]
            self.surface.blit(surface, rect)
        
        display.blit(self.surface, self.rect)
    
    def make_button(self, button_id, size, position, color, text, text_size=30, text_color=WHITE):
        button = Button(button_id, size, position, color, text, text_size, text_color)
        self.buttons.append(button)
            
    def make_surface(self, size, position, color=WHITE):
        surface = pygame.Surface(size)
        surface.fill(color)
        self.surfaces.append(surface)
        
        rect = surface.get_rect(center = position)
        self.rects.append(rect)
    
    def make_image(self, image_path, position, size=None):
        surface = pygame.image.load(image_path)
        if size != None:
            surface = pygame.transform.scale(surface, size)
        
        self.surfaces.append(surface)
        
        rect = surface.get_rect(center = position)
        self.rects.append(rect)
        
    def make_gif(self, folder_path, frames_per_image, position, size=None, loop=-1):
        gif = GIF(folder_path, frames_per_image, size, loop)
        self.gifs.append(gif)
        
        surface = gif.render_surface()
        rect = surface.get_rect(center = position)
        self.gifs_rects.append(rect)
        
    def make_text(self, text, size, position, color=WHITE, antiallias=False):
        font = pygame.font.Font(r'data\font\arcade-classic.TTF', size)
        text = font.render(text, antiallias, color)
        
        self.surfaces.append(text)
        
        rect = text.get_rect(center = position)
        self.rects.append(rect)
        
    def button_clicked(self, mouse_pos):
        for button in self.buttons:
            rect = button.rect
            
            if rect.collidepoint(mouse_pos):
                return button.id
            
        return None
        
    def surface_clicked(self, mouse_pos):
        size = len(self.surfaces)
        for i in range(size):
            rect = self.rects[i]
            
            if rect.collidepoint(mouse_pos):
                return self.surfaces[i]                
            
        return None
    