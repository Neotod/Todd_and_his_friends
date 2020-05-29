import pygame

class Button:
    ''' Make a button using pygame surface and rect
    
    in this class, button is a surface and it have many attributes of a rect like x, y, etc.
    
    '''
    
    def __init__(self, button_id, size, position=(0, 0), color=(255, 255, 255), text='button', text_size=30, text_collor=(0, 0, 0)):
        ''' make a button
        
        Keyword arguments:
        size --> size of the button(or size of the button's surface), it's mandatory
        position --> position of center of the button(center of button's surface rect), defualt is (0, 0)
        text --> button's text (text of that surface which is for showing text of button)
        text_size --> size of button's text
        text_collor --> collor of button's text
        collor --> collor of button
        
        '''
        self.id = button_id
        self.surface = pygame.Surface(size)
        self.surface.fill(color)
        self.rect = self.surface.get_rect(center=position)
        
        font = pygame.font.Font(r'data\font\arcade-classic.TTF', text_size)
        self.text_surf = font.render(text, True, text_collor)
        self.text_rect = self.text_surf.get_rect(center=position)
        
        self.x = self.rect.x
        self.y = self.rect.y
        self.center = self.rect.center
        self.width = self.rect.w
        self.height = self.rect.h
        
    def show(self, display):
        display.blit(self.surface, self.rect)
        display.blit(self.text_surf, self.text_rect)
        
    def is_clicked(self, mouse_pos):
        ''' Check if the button is clicked by the mouse
        
        This function must get used in a mouse event handler and event's type must be MOUSEBUTTONDOWN
        mouse_pos argument should be passed in the event handler with event.pos for event.type MOUSEBUTTONDOWN
        
        '''
        
        if self.rect.collidepoint(mouse_pos):
            return True
            
        return False