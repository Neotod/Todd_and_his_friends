import pygame
from data.sources.game import Game
from data.sources.files import Files

play_sound = Files.play_sound
get_path = Files.get_full_path

def start_again():
    global game
    del game
    game = Game()
    game.make_screens()
    game.setup()
    game.state = 'run'
    
    music_path = get_path('sounds', 'loops', 'No-Tomorrow')
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(loops=-1)

game = Game()
game.setup()
game.make_screens()
while True:
    if game.state == 'start':
        game.start()
        if game.state == 'run':
            start_again()
    elif game.state == 'run':
        game.loop()
    elif game.state == 'pause':
        game.pause()
    elif game.state == 'game-over':
        game.game_over()
    elif game.state == 'exit':
        break
    
pygame.quit()