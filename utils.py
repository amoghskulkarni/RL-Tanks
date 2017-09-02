import pygame
from pygame import error


def load_image(name, scale_x, scale_y):
    # Attempt to load the image
    try:
        image = pygame.image.load(name)
    except error, message:
        print 'Cannot load image:', name
        raise SystemExit, message

    # Makes a new copy of a Surface and converts its color format and depth to match the display
    image = image.convert()
    image = pygame.transform.scale(image, (scale_x, scale_y))

    return image, image.get_rect()
