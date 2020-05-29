import pygame

# constants
SCREEN_HEIGHT, SCREEN_WIDTH = 500, 900
GROUND_HEIGHT, GROUND_WIDTH = 563, 1000
BLACK = (0, 0, 0)

class Ground(pygame.sprite.Sprite):
    
    def __init__(self):
        super().__init__()
        self.surface = pygame.image.load(r'data\images\ground\ground.png')
        self.position = [SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 30]
        self.rect = self.surface.get_rect(center = tuple(self.position))
        
        self.void_surfs = []
        self.void_rects = []
        
        self.teleport_places_surfs = []
        self.teleport_places_rects = []
        self.teleport_places_init_positions = []
        
        self.swamp_surfs = []
        self.swamp_rects = []
        self.swamp_init_positions = []
        
        self.decoration_surfs = []
        self.decoration_rects = []
        self.decoration_init_positions = []
        
        self.tree_surfs = []
        self.tree_rects = []
        self.tree_init_positions = []
        
        self.enemy_born_place_surfs = []
        self.enemy_born_place_rects = []
        self.enemy_born_place_init_positions = []
        
    def update(self, keys, player, delta_t):
        player_pos = player.rect.center
        center_pos = self.position
        top_or_left_limit = -(0.05 * delta_t)
        changing_value = (0.03 * delta_t)
        
        if player.teleported == True:
            changing_value = 0
        
        if keys[pygame.K_s] == True and self.rect.bottom > SCREEN_HEIGHT:
            self.position[1] += -changing_value
        elif keys[pygame.K_w] == True and self.rect.top < top_or_left_limit:
            self.position[1] += changing_value
        elif keys[pygame.K_a] == True and self.rect.left < top_or_left_limit:
            right_offset = self.rect.right - 400
            if player_pos[0] <= right_offset:
                self.position[0] += changing_value
        elif keys[pygame.K_d] == True and self.rect.right > SCREEN_WIDTH:
            left_offset = self.rect.left + 400
            if player_pos[0] >= left_offset:
                self.position[0] += -changing_value
            
        if player.teleported == True:
            if player.teleport_place == 'healer':
                self.rect.right = SCREEN_WIDTH
                self.rect.bottom = SCREEN_HEIGHT
            elif player.teleport_place == 'alchemist':
                self.rect.left = 0
                self.rect.top = 0
            self.position = list(self.rect.center)
        else:
            self.rect.center = (int(self.position[0]), int(self.position[1]))
        
        self.void_rects[0].center = (GROUND_WIDTH // 2, self.rect.bottom - 10)
        self.void_rects[1].center = (self.rect.right - 10, GROUND_HEIGHT // 2)
        
        for i in range(len(self.swamp_rects)):
            center_x = self.rect.left + self.swamp_init_positions[i][0]
            center_y = self.rect.top + self.swamp_init_positions[i][1]
            self.swamp_rects[i].center = (center_x, center_y)
            
        for i in range(len(self.enemy_born_place_rects)):
            center_x = self.rect.left + self.enemy_born_place_init_positions[i][0]
            center_y = self.rect.top + self.enemy_born_place_init_positions[i][1]
            self.enemy_born_place_rects[i].center = (center_x, center_y)

        for i in range(len(self.tree_init_positions)):
            for j in range(len(self.tree_rects[i])):
                center_x = self.rect.left + self.tree_init_positions[i][j][0]
                center_y = self.rect.top + self.tree_init_positions[i][j][1]
                self.tree_rects[i][j].center = (center_x, center_y)
            
        for i in range(len(self.decoration_init_positions)):
            for j in range(len(self.decoration_rects[i])):
                center_x = self.rect.left + self.decoration_init_positions[i][j][0]
                center_y = self.rect.top + self.decoration_init_positions[i][j][1]
                self.decoration_rects[i][j].center = (center_x, center_y)
                
        for i in range(len(self.teleport_places_init_positions)):
            for j in range(len(self.teleport_places_surfs[i])):
                center_x = self.rect.left + self.teleport_places_init_positions[i][j][0]
                center_y = self.rect.top + self.teleport_places_init_positions[i][j][1]
                self.teleport_places_rects[i][j].center = (center_x, center_y)
        
    def show(self, display):
        display.blit(self.surface, self.rect)
        
        size = len(self.swamp_surfs)
        for i in range(size):
            swamp_surf = self.swamp_surfs[i]
            swamp_rect = self.swamp_rects[i]
            display.blit(swamp_surf, swamp_rect)
    
    def make_voids(self):
        void1_surface = pygame.Surface((GROUND_WIDTH, 32))
        void2_surface = pygame.Surface((32, GROUND_HEIGHT))
        
        self.void_surfs.append(void1_surface)
        self.void_surfs.append(void2_surface)
        
        for surface in self.void_surfs:
            surface.set_colorkey(BLACK)
            
        void1_rect = void1_surface.get_rect(center = (GROUND_WIDTH // 2, self.rect.bottom - 10))
        void2_rect = void2_surface.get_rect(center = (self.rect.right - 10, GROUND_HEIGHT // 2))
        
        self.void_rects.append(void1_rect)
        self.void_rects.append(void2_rect)
        
    def make_teleport_places(self):
        # make healer teleport places
        teleport_surf1 = pygame.Surface((30, 70))
        teleport_surf2 = pygame.Surface((120, 80))
        
        healer_teleport_surfs = (teleport_surf1, teleport_surf2)
        self.teleport_places_surfs.append(healer_teleport_surfs)
        
        teleport_init_pos = ((761, 450), (830, 440))
        self.teleport_places_init_positions.append(teleport_init_pos)
        
        center_pos = (self.rect.left + teleport_init_pos[0][0],
                        self.rect.top + teleport_init_pos[0][1])
        teleport_rect1 = teleport_surf1.get_rect(center = center_pos)
        
        center_pos = (self.rect.left + teleport_init_pos[1][0],
                        self.rect.top + teleport_init_pos[1][1])
        teleport_rect2 = teleport_surf2.get_rect(center = center_pos)
        
        healer_teleport_rects = (teleport_rect1, teleport_rect2)
        self.teleport_places_rects.append(healer_teleport_rects)
        
        # make alchemsit teleport places
        teleport_surf3 = pygame.Surface((163, 30))
        teleport_surf4 = pygame.Surface((85, 90))
        teleport_surf5 = pygame.Surface((80, 45))
        
        alchemist_teleport_surfs = (teleport_surf3, teleport_surf4, teleport_surf5)
        self.teleport_places_surfs.append(alchemist_teleport_surfs)
        
        teleport_init_pos = ((281, 25), (269, 70), (330, 113))
        self.teleport_places_init_positions.append(teleport_init_pos)
        
        center_pos = (self.rect.left + teleport_init_pos[0][0],
                        self.rect.top + teleport_init_pos[0][1])
        teleport_rect3 = teleport_surf3.get_rect(center = center_pos)
        
        center_pos = (self.rect.left + teleport_init_pos[1][0],
                        self.rect.top + teleport_init_pos[1][1])
        teleport_rect4 = teleport_surf4.get_rect(center = center_pos)
        
        center_pos = (self.rect.left + teleport_init_pos[2][0],
                        self.rect.top + teleport_init_pos[2][1])
        teleport_rect5 = teleport_surf5.get_rect(center = center_pos)

        alchemist_teleport_rects = (teleport_rect3, teleport_rect4, teleport_rect5)
        self.teleport_places_rects.append(alchemist_teleport_rects)
        
        for surfaces in self.teleport_places_surfs:
            for surface in surfaces:
                surface.fill(BLACK)
        
    def make_swamps(self):
        self.swamp_init_positions = [
            (30, 30), (230, 465), (250, 465), (280, 475), (400, 190), (422, 190),
            (635, 320), (660, 335), (660, 220), (890, 175), (920, 175)
        ]
        
        image_path = r'data\images\ground\swamp.png'
        swamp_image = pygame.image.load(image_path)
        for i in range(11):
            self.swamp_surfs.append(swamp_image)
            
            ground_rect = self.rect
            center_x = ground_rect.left + self.swamp_init_positions[i][0]
            center_y = ground_rect.top + self.swamp_init_positions[i][1]
            swamp_center = (center_x, center_y)
            
            swamp_rect = swamp_image.get_rect(center = swamp_center)

            self.swamp_rects.append(swamp_rect)

    def make_decorations(self):
        # make ridges
        ridge_init_positions = [
            (20, 40), (350, 197), (910, 175)
        ]
        ridge_surfs = []
        ridge_rects = []
        for i in range(3):
            image_path = r'data\images\ground\ridges\\' + str(i + 1) + '.png'
            image = pygame.image.load(image_path)
            ridge_surfs.append(image)
            
            ground_rect = self.rect
            center_x = ground_rect.left + ridge_init_positions[i][0]
            center_y = ground_rect.top + ridge_init_positions[i][1]
            ridge_center = (center_x, center_y)
            
            ridge_rect = image.get_rect(center = ridge_center)

            ridge_rects.append(ridge_rect)
            
        self.decoration_init_positions.append(ridge_init_positions)
        self.decoration_surfs.append(ridge_surfs)
        self.decoration_rects.append(ridge_rects)
        
        # make bushes
        bush_init_positions = [
            (5, 40), (380, 160), (620, 340), (230, 480)
        ]
        bush_surfs = []
        bush_rects = []
        for i in range(4):
            image_path = r'data\images\ground\bushes\\' + str(i + 1) + '.png'
            image = pygame.image.load(image_path)
            bush_surfs.append(image)
            
            ground_rect = self.rect
            center_x = ground_rect.left + bush_init_positions[i][0]
            center_y = ground_rect.top + bush_init_positions[i][1]
            bush_center = (center_x, center_y)
            
            bush_rect = image.get_rect(center = bush_center)

            bush_rects.append(bush_rect)
        
        self.decoration_init_positions.append(bush_init_positions)
        self.decoration_surfs.append(bush_surfs)
        self.decoration_rects.append(bush_rects)
        
    def make_trees(self):
        # make death trees
        tree_init_positions = [
            (65, 140), (280, 430)
        ]
        tree_surfs = []
        tree_rects = []
        for i in range(2):
            image_path = r'data\images\ground\trees\\' + str(i + 1) + '.png'
            tree_image = pygame.image.load(image_path)
            tree_surfs.append(tree_image)
            
            ground_rect = self.rect
            center_x = ground_rect.left + tree_init_positions[i][0]
            center_y = ground_rect.top + tree_init_positions[i][1]
            tree_center = (center_x, center_y)
            
            tree_rect = tree_image.get_rect(center = tree_center)

            tree_rects.append(tree_rect)
        
        self.tree_init_positions.append(tree_init_positions)
        self.tree_surfs.append(tree_surfs)
        self.tree_rects.append(tree_rects)
        
        # make willows:
        willow_init_positions = [
            (440, 160), (670, 300), (910, 140)
        ]
        willow_surfs = []
        willow_rects = []
        image_num = 1
        for i in range(3):
            image_path = r'data\images\ground\willows\\' + str(image_num) + '.png'
            image = pygame.image.load(image_path)
            image_num += 1
            
            willow_surfs.append(image)
            
            ground_rect = self.rect
            center_x = ground_rect.left + willow_init_positions[i][0]
            center_y = ground_rect.top + willow_init_positions[i][1]
            willow_center = (center_x, center_y)
            
            willow_rect = image.get_rect(center = willow_center)

            willow_rects.append(willow_rect)

        self.tree_init_positions.append(willow_init_positions)
        self.tree_surfs.append(willow_surfs)
        self.tree_rects.append(willow_rects)
            
    def make_enemy_born_places(self):
        self.enemy_born_place_init_positions = [
            (530, 170), (915, 230), (280, 330)
        ]

        # make graves (dirty and dusty born places)
        for i in range(2):
            image_path = r'data\images\enemy\child_enemy\grave' + str(i + 1) + '.png'
            image = pygame.image.load(image_path)
            self.enemy_born_place_surfs.append(image)
            
            ground_rect = self.rect
            center_x = ground_rect.left + self.enemy_born_place_init_positions[i][0]
            center_y = ground_rect.top + self.enemy_born_place_init_positions[i][1]
            grave_center = (center_x, center_y)
            
            grave_rect = image.get_rect(center = grave_center)

            self.enemy_born_place_rects.append(grave_rect)
        
        # make gate (child wiz born place)
        image_path = r'data\images\enemy\child_enemy\gate.png'
        image = pygame.image.load(image_path)
        self.enemy_born_place_surfs.append(image)

        ground_rect = self.rect
        center_x = ground_rect.left + self.enemy_born_place_init_positions[2][0]
        center_y = ground_rect.top + self.enemy_born_place_init_positions[2][1]
        grave_center = (center_x, center_y)
        
        grave_rect = image.get_rect(center = grave_center)

        self.enemy_born_place_rects.append(grave_rect)
        
    def is_player_collide_teleport_place(self, player_feet_pos):
        for rects in self.teleport_places_rects:
            for rect in rects:
                if rect.collidepoint(player_feet_pos) == True:
                    index = self.teleport_places_rects.index(rects)
                    if index == 0:
                        return 'healer'
                    elif index == 1:
                        return 'alchemist'
        
        return None
