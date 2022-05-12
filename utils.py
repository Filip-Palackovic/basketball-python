import pygame
import random
import os


def get_path(*directories):
    return os.path.join(os.path.dirname(__file__), "Resources", *directories)


def get_scale(size: int, real_size: int):
    return real_size / size


def get_real_size(scale: float, size: int):
    return size * scale


pygame.display.init()
WIDTH, HEIGHT = 1920, 1080
REAL_WIDTH, REAL_HEIGHT = (
    pygame.display.Info().current_w,
    pygame.display.Info().current_h,
)
W_SCALE = get_scale(WIDTH, REAL_WIDTH)
H_SCALE = get_scale(HEIGHT, REAL_HEIGHT)


class Images:

    background: pygame.Surface = None
    basket: pygame.Surface = None
    ball: pygame.Surface = None
    net: pygame.Surface = None
    game_over: pygame.Surface = None

    @classmethod
    def load_images(cls):
        def get_size_width(size: int):
            return get_real_size(W_SCALE, size)

        w = get_size_width

        def get_size_height(size: int):
            return get_real_size(H_SCALE, size)

        h = get_size_height

        def transform_image(image: pygame.Surface) -> pygame.Surface:
            return pygame.transform.scale(
                image, (w(image.get_width()), h(image.get_height()))
            )

        cls.background = transform_image(
            pygame.image.load(get_path("Images", "background.png")).convert_alpha()
        )

        cls.basket = transform_image(
            pygame.image.load(get_path("Images", "basket.png")).convert_alpha()
        )

        cls.ball = transform_image(
            pygame.image.load(get_path("Images", "ball.png")).convert_alpha()
        )

        cls.net = transform_image(
            pygame.image.load(get_path("Images", "net.png")).convert_alpha()
        )
        cls.game_over = transform_image(
            pygame.image.load(
                get_path("Images", "game over screen.png")
            ).convert_alpha()
        )


class Fonts:

    pygame.font.init()
    burbank = pygame.font.Font(
        get_path("Fonts", "BurbankBigCondensed-Bold.otf"),
        int(get_real_size(W_SCALE, 120)),
    )


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
    VALID_X = (int(game.X_START + game.w(70)), int(game.X_START + game.w(1300)))
    VALID_Y = (int(game.h(30)), int(game.h(800)))

    while pygame.Rect(0, 0, game.w(game.X_START + 548), game.h(175)).collidepoint(
        coords := (random.randint(*VALID_X), random.randint(*VALID_Y))
    ):
        coords = random.randint(*VALID_X), random.randint(*VALID_Y)

    return coords
