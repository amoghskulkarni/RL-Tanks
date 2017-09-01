from pygame.locals import *
from game_objects import *


class Game:
    def __init__(self, length=800, width=800):
        # Save the parameters of the simulation
        self.canvas_length = length             # Default is 800
        self.canvas_width = width               # Default is 800

        # Initialize pygame library
        pygame.init()

        # Initialize the window, set caption
        self.screen = pygame.display.set_mode((self.canvas_length, self.canvas_width))
        pygame.display.set_caption('Reinforcement Learning: Tanks')

        # Create a new surface to be used as a background for setting caption, HUD and other stuff
        bg = pygame.Surface(self.screen.get_size())
        # convert with no arguments will make sure our background is the same format as the display window
        self.background = bg.convert()
        # Set the color as black
        self.background.fill((0, 0, 0))

        if pygame.font:
            font = pygame.font.Font(None, 36)
            text = font.render("The tank which shoots down the other, wins.", 1, (255, 255, 255))
            text_pos = text.get_rect(centerx=self.background.get_width() / 2, centery=30)
            self.background.blit(text, text_pos)
            text = font.render("Press Esc to start.", 1, (255, 255, 255))
            text_pos = text.get_rect(centerx=self.background.get_width() / 2, centery=60)
            self.background.blit(text, text_pos)

        # blit() superimposes the Surface() objects on one another and flip() swaps the double/single buffered displays
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

        self.players = []
        for i in range(2):
            if i == 0:
                self.players.append(Player(game_obj=self, init_direction=90, x=10, y=10))
            else:
                self.players.append(Player(game_obj=self, init_direction=270, x=750, y=750))

        self.all_player_sprites = pygame.sprite.RenderPlain(tuple(self.players))
        self.all_projectile_sprites = pygame.sprite.RenderPlain(tuple([]))
        self.clock = pygame.time.Clock()

    def run(self):
        show_title = True
        while show_title:
            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    show_title = False
                    self.background.fill((0, 0, 0))

        going = True
        while going:
            # This will ensure that the game doesn't run faster than 60 FPS
            self.clock.tick(60)

            keys = pygame.key.get_pressed()
            if keys[K_w]:
                for p in self.players:
                    p.move_fwd = 1
            if keys[K_s]:
                for p in self.players:
                    p.move_rev = 1

            for event in pygame.event.get():
                if event.type == QUIT:
                    going = False
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    going = False
                elif event.type == KEYDOWN and event.key == K_a:
                    for p in self.players:
                        p.rotate_clock = 1
                elif event.type == KEYDOWN and event.key == K_d:
                    for p in self.players:
                        p.rotate_anticlock = 1
                elif event.type == KEYDOWN and event.key == K_SPACE:
                    for p in self.players:
                        p.fire_projectile = 1

            # Call update methods of all the sprites
            self.all_player_sprites.update()
            self.all_projectile_sprites.update()

            self.screen.blit(self.background, (0, 0))
            self.all_player_sprites.draw(self.screen)
            self.all_projectile_sprites.draw(self.screen)
            pygame.display.flip()