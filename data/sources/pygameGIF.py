from os import listdir, path
import pygame

class GIF:
    
    def __init__(self, folder_path : str, frames_per_image=1, image_size=None, loop=-1):
        self.image_size = image_size
        self.frames_per_image = frames_per_image
        self.current_frame = 1
        
        self.animation_images = []
        self.animation_index = 0
        self.animation_index_limit = 0
        
        self.folder_path = folder_path
        
        self.loop = loop
        self.current_loop = 0
        
        self.set_images(folder_path)
        
    def set_images(self, folder_path):
        images = listdir(folder_path)
        for image in images:
            self.animation_images.append(image)
        
        key_function = lambda string : int(string[:-4])
        self.animation_images.sort(key=key_function)
        self.animation_index_limit = len(self.animation_images)
        
    def render_surface(self, convert = False):
        image_path = path.join(self.folder_path, self.animation_images[self.animation_index])
        image = pygame.image.load(image_path)
        if self.image_size == None:
            self.surface = image
        else:
            self.surface = pygame.transform.scale(image, self.image_size)
            
        if self.current_frame == self.frames_per_image:
            if self.animation_index < self.animation_index_limit:
                self.animation_index += 1
            self.current_frame = 0
        else:
            self.current_frame += 1
            
        if self.loop == -1:
            if self.animation_index == self.animation_index_limit:
                self.animation_index = 0
        elif self.current_loop < self.loop:
            if self.animation_index == self.animation_index_limit:
                self.animation_index = 0
                self.current_loop += 1
            
        return self.surface