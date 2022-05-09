import pygame
import random
import math
import os


def get_path(*directories):
    return os.path.join(os.path.dirname(__file__), "Resources", *directories)


class Images:

    background: pygame.Surface = None
    basket: pygame.Surface = None
    ball: pygame.Surface = None
    net: pygame.Surface = None
    game_over: pygame.Surface = None

    @classmethod
    def load_images(cls):
        cls.background = pygame.image.load(
            get_path("Images", "background.png")
        ).convert_alpha()
        cls.basket = pygame.image.load(get_path("Images", "basket.png")).convert_alpha()
        cls.ball = pygame.image.load(get_path("Images", "ball.png")).convert_alpha()
        cls.net = pygame.image.load(get_path("Images", "net.png")).convert_alpha()
        cls.game_over = pygame.image.load(
            get_path("Images", "game over screen.png")
        ).convert_alpha()


class Fonts:

    pygame.font.init()
    burbank = pygame.font.Font(get_path("Fonts", "BurbankBigCondensed-Bold.otf"), 120)


class Sounds:
    pygame.mixer.init()

    game_over = pygame.mixer.Sound(get_path("Sounds", "game over.wav"))
    highest_score = pygame.mixer.Sound(get_path("Sounds", "highest score.wav"))
    score = pygame.mixer.Sound(get_path("Sounds", "score.wav"))
    launch = pygame.mixer.Sound(get_path("Sounds", "launch.wav"))


def convert_to_pygame(p):
    size = Images.ball.get_size()
    return int(p.x) - size[1] / 2, -int(-p.y) - size[1] / 2


def rot_center(image, angle):
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image


def measure_distance(xo, yo, x, y):
    dx = x - xo
    dy = y - yo
    return ((dx**2) + (dy**2)) ** 0.5


def get_random_position(game):
    VALID_X = (game.X_START + 30, game.X_START + 1300)
    VALID_Y = (30, 820)

    while pygame.Rect(0, 0, game.X_START + 548, 154).collidepoint(
        coords := (random.randint(*VALID_X), random.randint(*VALID_Y))
    ):
        coords = random.randint(*VALID_X), random.randint(*VALID_Y)

    return coords
