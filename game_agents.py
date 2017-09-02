from pygame.locals import *


class HumanAgent:
    def __init__(self, name, game_obj):
        self.name = name
        self.game = game_obj
        self.sprite = None
        self.score = 0

    def take_action(self, **kwargs):
        keys = []
        events = []
        # Parse kwargs
        for kwarg in kwargs:
            if kwarg == "keys":
                keys = kwargs[kwarg]
            elif kwarg == "events":
                events = kwargs[kwarg]
            else:
                raise KeyError

        # Check what keys are pressed, take an action accordingly
        if keys[K_w]:
            self.sprite.move_fwd = True
        if keys[K_s]:
            self.sprite.move_rev = True

        for event in events:
            if event.type == KEYDOWN and event.key == K_a:
                self.sprite.rotate_clock = True
            elif event.type == KEYDOWN and event.key == K_d:
                self.sprite.rotate_anticlock = True
            elif event.type == KEYDOWN and event.key == K_SPACE:
                self.sprite.fire_projectile = True


class RLAgent:
    def __init__(self, name, game_obj):
        self.name = name
        self.game = game_obj
        self.sprite = None
        self.score = 0

    def take_action(self, **kwargs):
        pass
