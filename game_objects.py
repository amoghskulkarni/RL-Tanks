import pygame
from utils import load_image


class Tank(pygame.sprite.Sprite):
    def __init__(self, game_obj, image_name, init_direction, agent, x, y):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer

        self.image, self.rect = load_image(name=image_name, scale_x=32, scale_y=32)

        self.game = game_obj
        self.direction = init_direction
        self.rect.topleft = x, y

        self.original = self.image
        self.area = self.game.screen.get_rect()

        # Save the self-reference into agent that controls this tank
        self.agent = agent
        self.agent.sprite = self

        rotate = pygame.transform.rotate
        self.image = rotate(self.original, self.direction)

    def rotate90(self, rotation):
        if rotation >= 'clockwise':
            self.direction += 90
            if self.direction == 360:
                self.direction = 0
                self.image = self.original
            elif self.direction < 0:
                self.direction += 360
        elif rotation == 'anticlockwise':
            self.direction -= 90
            if self.direction == 360:
                self.direction = 0
                self.image = self.original
            elif self.direction < 0:
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

        projectile = Projectile(game_obj=self.game, start_x=proj_x, start_y=proj_y, move_direction=self.direction)
        projectile.agent = self.agent

        self.game.all_projectile_sprites.add(projectile)

    def update(self):
        # Move the control logic to the agent's take_action() method
        pass


class Projectile(pygame.sprite.Sprite):
    def __init__(self, game_obj, start_x, start_y, move_direction):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        init_position_dir = {0: (start_x, start_y - 4), 90: (start_x - 4, start_y),
                             180: (start_x, start_y + 4), 270: (start_x + 4, start_y)}

        self.game = game_obj
        self.image, self.rect = load_image(name='images/projectile.bmp', scale_x=4, scale_y=4)
        self.area = self.game.screen.get_rect()

        self.direction = move_direction

        # Placeholder for the agent that is going to control this tank
        self.agent = None

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
        tanks_hit = pygame.sprite.spritecollide(sprite=self, group=self.game.all_player_sprites, dokill=False)

        # If the tank that is hit is enemy, increment the score for each of them
        for tank in tanks_hit:
            if tank.agent is self.agent:
                self.agent.score -= 2
            else:
                self.agent.score += 1
            tank.kill()

            # TODO: Make round_over True, only if the list self.all_player_sprites contains sprites controlled by the same agent
            round_over = True

            if round_over:
                self.game.round_not_over = False
                for alive_tank in self.game.all_player_sprites:
                    alive_tank.kill()

        if self.touched_to_edge or len(tanks_hit) > 0:
            self.kill()
        else:
            self.move()


class HUD(pygame.sprite.Sprite):
    def __init__(self, game_obj):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.game = game_obj

    def update(self):
        self.game.background.fill((0, 0, 0))

        font = pygame.font.Font(None, 36)
        column_width = self.game.background.get_width() / len(self.game.player_agents)

        for i, agent in enumerate(self.game.player_agents):
            text = font.render(agent.name + ': ' + str(agent.score), 1, (255, 255, 255))
            text_pos = text.get_rect(centerx=i*column_width + column_width / 2, centery=30)

            self.game.background.blit(text, text_pos)

        self.game.screen.blit(self.game.background, (0, 0))
        pygame.display.flip()
