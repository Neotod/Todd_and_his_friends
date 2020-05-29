import pygame
    
def play_sound(file_path, volume=1, loops=0):
    sound = pygame.mixer.Sound(file_path)
    sound.set_volume(volume)
    sound.play(loops)