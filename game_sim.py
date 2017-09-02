import pygame
from game_objects import Tank, HUD
from game_agents import *


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

        # Bookkeeping for players (i.e. playable sprites) and the agents that control them
        self.players = []
        self.player_agents = []

        # Create a tank for the human agent
        tank1 = Tank(game_obj=self, image_name='images/tank1.bmp', init_direction=90, x=10, y=10)
        self.players.append(tank1)
        self.player_agents.append(HumanAgent(name='Human', game_obj=self, sprite=tank1))

        # Create a tank for the computer agent
        tank2 = Tank(game_obj=self, image_name='images/tank2.bmp', init_direction=270, x=750, y=750)
        self.players.append(tank2)
        self.player_agents.append(RLAgent(name='RL Agent', game_obj=self, sprite=tank2))

        # Create all sprites (except projectiles)
        self.all_player_sprites = pygame.sprite.RenderPlain(tuple(self.players))
        self.all_projectile_sprites = pygame.sprite.RenderPlain(())

        # Create an HUD
        self.hud_sprite = HUD(game_obj=self)

        # Create a clock
        self.clock = pygame.time.Clock()

    def play_round(self):
        round_not_over = True
        game_running = True

        while round_not_over:
            # This will ensure that the game doesn't run faster than 60 FPS
            self.clock.tick(60)

            keys = pygame.key.get_pressed()
            events = pygame.event.get()

            # Check for "quit" events
            for event in events:
                if event.type == QUIT:
                    game_running = False
                    round_not_over = False
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    game_running = False
                    round_not_over = False

            # Tell agents to take actions
            for agent in self.player_agents:
                if isinstance(agent, HumanAgent):
                    agent.take_action(keys=keys, events=events)
                elif isinstance(agent, RLAgent):
                    agent.take_action()

            # Call update methods of all the sprites
            self.all_player_sprites.update()
            self.all_projectile_sprites.update()

            # Update the player sprites and projectiles
            self.screen.blit(self.background, (0, 0))
            self.all_player_sprites.draw(self.screen)
            self.all_projectile_sprites.draw(self.screen)
            pygame.display.flip()

        return game_running

    def show_welcome_screen(self):
        if pygame.font:
            font = pygame.font.Font(None, 36)
            text = font.render("The tank which shoots down the other, wins.", 1, (255, 255, 255))
            text_pos = text.get_rect(centerx=self.background.get_width() / 2, centery=30)
            self.background.blit(text, text_pos)
            text = font.render("Press Enter to start.", 1, (255, 255, 255))
            text_pos = text.get_rect(centerx=self.background.get_width() / 2, centery=60)
            self.background.blit(text, text_pos)

        # blit() superimposes the Surface() objects on one another and flip() swaps the double/single buffered displays
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

        show_title = True
        while show_title:
            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_RETURN:
                    show_title = False
                    self.background.fill((0, 0, 0))
                    self.hud_sprite.update()

    def run(self):
        self.show_welcome_screen()

        going = True
        while going:
            # Keep playing rounds until the end condition is hit
            going = self.play_round()

            # Update the HUD after each round
            self.hud_sprite.update()

        # Print winner on the screen

