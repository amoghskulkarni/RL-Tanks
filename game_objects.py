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
        if move_direction == 'forward':
            if self.direction == 0:
                new_pos = self.rect.move(0, -1)
            elif self.direction == 90:
                new_pos = self.rect.move(-1, 0)
            elif self.direction == 180:
                new_pos = self.rect.move(0, 1)
            elif self.direction == 270:
                new_pos = self.rect.move(1, 0)
        elif move_direction == 'reverse':
            if self.direction == 0:
                new_pos = self.rect.move(0, 1)
            elif self.direction == 90:
                new_pos = self.rect.move(1, 0)
            elif self.direction == 180:
                new_pos = self.rect.move(0, -1)
            elif self.direction == 270:
                new_pos = self.rect.move(-1, 0)
        if self.area.contains(new_pos):
            self.rect = new_pos

    def fire(self):
        # Create a projectile at the tip, and append it to the game's sprite list
        proj_x, proj_y = self.rect.midtop
        if self.direction == 90:
            proj_x, proj_y = self.rect.midleft
        elif self.direction == 180:
            proj_x, proj_y = self.rect.midbottom
        elif self.direction == 270:
            proj_x, proj_y = self.rect.midright
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

        self.image, self.rect = load_image(name='images/projectile.bmp', scale_x=4, scale_y=4)

        self.game = game_obj
        self.direction = move_direction

        if self.direction == 0:
            self.rect.center = start_x, start_y - 4
        elif self.direction == 90:
            self.rect.center = start_x - 4, start_y
        elif self.direction == 180:
            self.rect.center = start_x, start_y + 4
        elif self.direction == 270:
            self.rect.center = start_x + 4, start_y

        self.area = self.game.screen.get_rect()

        self.touched_to_edge = False

    def move(self):
        new_pos = None

        if self.direction == 0:
            new_pos = self.rect.move(0, -10)
        elif self.direction == 90:
            new_pos = self.rect.move(-10, 0)
        elif self.direction == 180:
            new_pos = self.rect.move(0, 10)
        elif self.direction == 270:
            new_pos = self.rect.move(10, 0)

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
