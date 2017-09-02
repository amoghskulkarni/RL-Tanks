import pygame
from utils import load_image


class Tank(pygame.sprite.Sprite):
    def __init__(self, game_obj, image_name, init_direction, x, y):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer

        self.image, self.rect = load_image(name=image_name, scale_x=32, scale_y=32)

        self.game = game_obj
        self.direction = init_direction
        self.rect.topleft = x, y

        self.original = self.image
        self.area = self.game.screen.get_rect()

        self.rotate_clock = False
        self.rotate_anticlock = False
        self.move_fwd = False
        self.move_rev = False
        self.fire_projectile = False

        rotate = pygame.transform.rotate
        self.image = rotate(self.original, self.direction)

    def rotate90(self, rotation):
        if rotation >= 'clockwise':
            self.direction += 90
            if self.direction == 360:
                self.direction = 0
                self.image = self.original
            if self.direction < 0:
                self.direction += 360
        elif rotation == 'anticlockwise':
            self.direction -= 90
            if self.direction == 360:
                self.direction = 0
                self.image = self.original
            if self.direction < 0:
                self.direction += 360
        rotate = pygame.transform.rotate
        self.image = rotate(self.original, self.direction)

    def move(self, move_direction):
        # If the direction which it is being moved in is 'forward', depending upon the
        new_pos = None
        forward_move_dir = {0: (0, -1), 90: (-1, 0), 180: (0, 1), 270: (1, 0)}
        reverse_move_dir = {0: (0, 1), 90: (1, 0), 180: (0, -1), 270: (-1, 0)}

        if move_direction == 'forward':
            new_pos = self.rect.move(forward_move_dir[self.direction])
        elif move_direction == 'reverse':
            new_pos = self.rect.move(reverse_move_dir[self.direction])

        # If tank's new position is still in the canvas, move the tank
        if self.area.contains(new_pos):
            self.rect = new_pos

    def fire(self):
        fire_actions_dir = {0: self.rect.midtop, 90: self.rect.midleft,
                            180: self.rect.midbottom, 270: self.rect.midright}

        # Create a projectile at the tip, and append it to the game's sprite list
        proj_x, proj_y = fire_actions_dir[self.direction]

        self.game.all_projectile_sprites.add(Projectile(game_obj=self.game,
                                                        start_x=proj_x, start_y=proj_y,
                                                        move_direction=self.direction))

    def update(self):
        if self.rotate_clock:
            self.rotate_clock = False
            self.rotate90(rotation='clockwise')
        if self.rotate_anticlock:
            self.rotate_anticlock = False
            self.rotate90(rotation='anticlockwise')
        if self.move_fwd:
            self.move_fwd = False
            self.move(move_direction='forward')
        if self.move_rev:
            self.move_rev = False
            self.move(move_direction='reverse')
        if self.fire_projectile:
            self.fire_projectile = False
            self.fire()


class Projectile(pygame.sprite.Sprite):
    def __init__(self, game_obj, start_x, start_y, move_direction):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        init_position_dir = {0: (start_x, start_y - 4), 90: (start_x - 4, start_y),
                             180: (start_x, start_y + 4), 270: (start_x + 4, start_y)}

        self.game = game_obj
        self.image, self.rect = load_image(name='images/projectile.bmp', scale_x=4, scale_y=4)
        self.area = self.game.screen.get_rect()

        self.direction = move_direction

        self.rect.center = init_position_dir[self.direction]

        self.touched_to_edge = False

    def move(self):
        move_direction_dir = {0: (0, -10), 90: (-10, 0), 180: (0, 10), 270: (10, 0)}

        new_pos = self.rect.move(move_direction_dir[self.direction])

        if self.area.contains(new_pos):
            self.rect = new_pos
        else:
            self.touched_to_edge = True

    def update(self):
        pygame.sprite.groupcollide(groupa=self.game.all_projectile_sprites,
                                   groupb=self.game.all_player_sprites,
                                   dokilla=True,
                                   dokillb=True)
        if not self.touched_to_edge:
            self.move()
        else:
            self.kill()


class HUD(pygame.sprite.Sprite):
    def __init__(self, game_obj):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.game = game_obj

    def update(self):
        font = pygame.font.Font(None, 36)
        column_width = self.game.background.get_width() / len(self.game.player_agents)

        for i, agent in enumerate(self.game.player_agents):
            text = font.render(agent.name + ': ' + str(agent.score), 1, (255, 255, 255))
            text_pos = text.get_rect(centerx=i*column_width + column_width / 2, centery=30)

            self.game.background.blit(text, text_pos)

        self.game.screen.blit(self.game.background, (0, 0))
        pygame.display.flip()
