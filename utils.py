import pygame
from pygame import error
from pygame.locals import RLEACCEL


def load_image(name, scale_x, scale_y, colorkey=None):
    # Attempt to load the image
    try:
        image = pygame.image.load(name)
    except error, message:
        print 'Cannot load image:', name
        raise SystemExit, message

    # Makes a new copy of a Surface and converts its color format and depth to match the display
    image = image.convert()
    image = pygame.transform.scale(image, (scale_x, scale_y))

    # Covert the image as per the color key passed as an argument
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)

    return image, image.get_rect()
