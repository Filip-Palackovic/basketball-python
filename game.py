import pygame
import pymunk
import pymunk.pygame_util
import json
import time
import math
from pygame.locals import *
from utils import (
    Fonts,
    Images,
    Sounds,
    measure_distance,
    convert_to_pygame,
    rot_center,
    get_random_position,
    get_path,
    get_scale,
    get_real_size,
)


class Match:
    def __init__(self, **kwargs) -> None:
        self.game: Game = kwargs.get("game")
        self.ball: pymunk.Shape = None
        self.scored: bool = False
        self.sound: bool = False
        self.collision_1: bool = False
        self.collision_2: bool = False
        self.invalid: bool = False
        self.clicked: bool = True
        self.remaining_time: int = None
        self.start_time: int = time.time()

    def restart(self) -> None:
        self.game.space.remove(self.ball)
        self.game.screen = "game"
        self.ball = None
        self.scored = False
        self.sound = False
        self.collision_1 = False
        self.collision_2 = False
        self.invalid = False
        self.clicked = True
        self.remaining_time = None
        self.start_time = time.time()


class Game:
    pygame.display.init()

    WIDTH, HEIGHT = 1920, 1080
    REAL_WIDTH, REAL_HEIGHT = (
        pygame.display.Info().current_w,
        pygame.display.Info().current_h,
    )
    W_SCALE = get_scale(WIDTH, REAL_WIDTH)
    H_SCALE = get_scale(HEIGHT, REAL_HEIGHT)

    WINDOW = pygame.display.set_mode(
        (WIDTH, HEIGHT), pygame.RESIZABLE | pygame.FULLSCREEN
    )

    Images.load_images()

    X_START = int(REAL_WIDTH / 2 - Images.background.get_size()[0] / 2)
    X_END = int(REAL_WIDTH / 2 + Images.background.get_size()[0] / 2)
    FLOOR_HEIGHT = 888
    DRAW_OPTIONS = pymunk.pygame_util.DrawOptions(WINDOW)

    FPS = 60
    DT = 1 / FPS

    def __init__(self) -> None:
        self.run = True
        self.debug = False

        self.space = pymunk.Space()
        self.space.gravity = (0, 981)
        self.angle: int = 0
        self.mouse_distance: int = 0
        self.mouse_pressed: bool = False
        self.x_mouse: int = 0
        self.y_mouse: int = 0
        self.score = 0
        self.r_disabled = False
        self.highest_score = json.load(
            open(__file__.replace("game.py", "scores.json"))
        )["highest_score"]
        self.screen: str = "game"
        self.match = Match(game=self)
        self.w = self.get_size_width
        self.h = self.get_size_height

    def get_size_width(self, size: int):
        return get_real_size(self.W_SCALE, size)

    def get_size_height(self, size: int):
        return get_real_size(self.H_SCALE, size)

    def load_music(self):
        pygame.mixer.init()
        pygame.mixer.music.load(get_path("Sounds", "Rainbow road Mario Kart DS.mp3"))
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(1)

    def create_boundaries(self):
        rects = [
            [
                (self.X_START - self.w(50), self.h(self.HEIGHT / 2)),
                (self.w(100), self.h(self.HEIGHT)),
            ],
            [
                (self.X_END + self.w(50), self.h(self.HEIGHT / 2)),
                (self.w(100), self.h(self.HEIGHT)),
            ],
            [
                (self.w(self.WIDTH / 2), self.h(0 - 50)),
                (self.w(self.WIDTH), self.h(100)),
            ],
            [
                (self.w(self.WIDTH / 2), self.h(self.FLOOR_HEIGHT + 50)),
                (self.w(self.WIDTH), self.h(100)),
            ],
            [
                (self.w(1464 + self.X_START), self.h(265)),
                (self.w(6), self.h(6)),
            ],  #  Basket hoop
            [
                (
                    self.w((1640 + 1692) / 2 + self.X_START),
                    self.h((582 + self.FLOOR_HEIGHT) / 2),
                ),
                (self.w(1692 - 1639), self.h(self.FLOOR_HEIGHT - 582)),
            ],  # Big basket base rectangle
            [
                (self.w(1651 + self.X_START), self.h(567)),
                (self.w(42), self.h(10)),
            ],  # Basket base "triangle"
            [
                (self.w(self.X_START + 1666.5), self.h(404)),
                (self.w(24), self.h(276)),
            ],  # Small basket base rectangle
            [
                (self.w((1630 + 1654) / 2 + self.X_START), self.h((72 + 376) / 2)),
                (self.w(26), self.h(305)),
            ],  # Basket board
            [
                (self.w(1471 + 36 / 2 + self.X_START), self.h(274 + 140 / 2)),
                (self.w(5), self.h(140)),
            ],  # Basket net left hitbox
            [
                (self.w(self.X_START + 1585 + 33 / 2), self.h(339.5)),
                (self.w(5), self.h(133)),
            ],  # Basket net right hitbox
        ]

        for index, payload in enumerate(rects):
            pos, size = payload
            pymunk.Body.KINEMATIC
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            body.position = pos

            shape = pymunk.Poly.create_box(body, size)
            shape.elasticity = 0.8
            shape.friction = 1
            shape.color = pygame.Color(124, 195, 2, 100)

            if index == 6:
                body.angle = -1.2217304
            elif index == 8:
                shape.elasticity = 0.2
            elif index == 9:
                body.angle = -3.4103733584
                shape.elasticity = 0.2
            elif index == 10:
                body.angle = -2.8989918876
                shape.elasticity = 0.2

            self.space.add(body, shape)

    def create_ball(self):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = get_random_position(self)
        shape = pymunk.Circle(body, self.w(30), (0, 0))
        shape.mass = 10
        shape.color = (255, 0, 0, 100)
        shape.elasticity = 0.9
        shape.friction = 1
        self.space.add(body, shape)
        self.match.ball = shape

    def sling_action(self):
        ball_x, ball_y = self.match.ball.body.position
        max_lenght = 250

        self.mouse_distance = measure_distance(
            ball_x, ball_y, self.x_mouse, self.y_mouse
        )
        if self.mouse_distance < max_lenght:
            self.mouse_distance += 10

        dy = self.y_mouse - ball_y
        dx = self.x_mouse - ball_x
        if dx == 0:
            dx = 0.00000000000001
        return math.atan((float(dy)) / dx), self.mouse_distance

    def update_highest_score(self):
        if self.score > self.highest_score:
            json.dump(
                {"highest_score": self.score},
                open(__file__.replace("game.py", "scores.json"), "w"),
            )
            self.highest_score = self.score
            return True

    def handle_screens(self):
        if (
            isinstance(self.match.remaining_time, float)
            and time.time() > self.match.remaining_time
        ):
            if self.match.scored:
                self.match.restart()
            else:
                new_score = self.update_highest_score()
                self.screen = "game over"
                pygame.mixer.music.stop()
                if new_score and not self.match.sound:
                    Sounds.highest_score.play()
                    self.match.sound = True
                elif not self.match.sound:
                    Sounds.game_over.play()
                    self.match.sound = True

    def handle_keydowns(self, event: pygame.event.Event):
        if (event.type == pygame.QUIT) or (event.type == KEYDOWN and event.key == K_F4):
            self.run = False
        if event.type == KEYDOWN:
            if event.key == K_p:
                self.r_disabled = not self.r_disabled
            if event.key == K_r and not self.r_disabled:
                self.match.restart()
            elif event.key == K_t:
                self.update_highest_score()
                self.screen = "game over"

    def handle_mouse_events(self, event: pygame.event.Event):
        if self.match.ball:
            x, y = self.match.ball.body.position
            if (
                pygame.mouse.get_pressed()[0]
                and self.x_mouse > (x - 280)
                and self.x_mouse < (x + 280)
                and self.y_mouse > (y - 280)
                and self.y_mouse < (y + 280)
            ) and self.match.clicked:
                self.mouse_pressed = True
        if (
            event.type == pygame.MOUSEBUTTONUP
            and event.button == 1
            and self.mouse_pressed
        ):
            self.mouse_pressed = False

    def handle_game_over_buttons(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.match.clicked = True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.screen == "game over":
                replay_button_vertical = pygame.Rect(
                    self.w(self.X_START + 181), self.h(681), self.w(129), self.h(218)
                )
                replay_button_horizontal = pygame.Rect(
                    self.w(self.X_START + 136), self.h(725), self.w(218), self.h(129)
                )

                if pygame.mouse.get_pressed()[0] and (
                    replay_button_vertical.collidepoint(self.x_mouse, self.y_mouse)
                    or replay_button_horizontal.collidepoint(self.x_mouse, self.y_mouse)
                ):
                    Sounds.launch.play()
                    self.screen = "game"
                    self.score = 0
                    self.match.restart()
                    self.load_music()
                    self.match.clicked = False

                quit_button_vertical = pygame.Rect(
                    self.w(self.X_START + 1398), self.h(679), self.w(129), self.h(218)
                )
                quit_button_horizontal = pygame.Rect(
                    self.w(self.X_START + 1355), self.h(723), self.w(218), self.h(129)
                )

                if pygame.mouse.get_pressed()[0] and (
                    quit_button_vertical.collidepoint(self.x_mouse, self.y_mouse)
                    or quit_button_horizontal.collidepoint(self.x_mouse, self.y_mouse)
                ):
                    Sounds.launch.play()
                    self.run = False

    def handle_events(self):
        for event in pygame.event.get():
            self.handle_keydowns(event)

            self.handle_mouse_events(event)

            self.handle_game_over_buttons(event)

    def handle_ball_launch(self):
        if self.mouse_pressed and self.match.ball.body.body_type == pymunk.Body.STATIC:
            self.angle, self.mouse_distance = self.sling_action()
            self.mouse_distance = min(self.mouse_distance, 250)

        elif (
            self.match.ball.body.body_type == pymunk.Body.STATIC and self.mouse_distance
        ):
            if (
                self.match.start_time + 0.5 > time.time()
            ):  # Avoids the ball from being launched when clicking the restart button.
                self.mouse_distance = 0
                self.angle = 0
                return
            self.match.ball.body.body_type = pymunk.Body.DYNAMIC
            if self.x_mouse >= self.match.ball.body.position.x + 5:
                self.mouse_distance = -self.mouse_distance
            power = self.w(self.mouse_distance) * 65
            impulse = power * pymunk.Vec2d(1, 0)
            self.match.ball.body.apply_impulse_at_local_point(
                impulse.rotated(self.angle)
            )
            Sounds.launch.play()
            self.match.remaining_time = time.time() + 5
            self.mouse_distance = 0
            self.angle = 0

    def count_score(self):
        if not self.match.ball or self.match.ball.body.body_type != pymunk.Body.DYNAMIC:
            return
        pos = convert_to_pygame(self.match.ball.body.position)
        ball_rect = pygame.Rect(*pos, *Images.ball.get_size())

        rect_1 = pygame.Rect(
            self.w(self.X_START + 1506), self.h(320), self.w(74), self.h(4)
        )
        rect_2 = pygame.Rect(
            self.w(self.X_START + 1505), self.h(372), self.w(58), self.h(4)
        )

        self.match.collision_1 = self.match.collision_1 or ball_rect.colliderect(rect_1)
        if self.match.collision_1:
            self.match.collision_2 = self.match.collision_2 or ball_rect.colliderect(
                rect_2
            )
        elif ball_rect.colliderect(rect_2):
            self.match.invalid = True

        if (
            self.match.collision_1
            and self.match.collision_2
            and not self.match.scored
            and not self.match.invalid
        ):
            self.score += 1
            Sounds.score.play()
            self.match.remaining_time = time.time() + 1.5
            self.match.scored = True

    def draw_game(self):
        self.WINDOW.blit(Images.background, (self.X_START, 0))

        if self.match.ball:
            pos = convert_to_pygame(self.match.ball.body.position)
            image = rot_center(Images.ball, math.degrees(self.match.ball.body.angle))
            self.WINDOW.blit(image, pos)

        self.WINDOW.blit(Images.net, (self.w(1445 + self.X_START), self.h(0)))

        self.WINDOW.blit(Images.basket, (self.w(1445 + self.X_START), self.h(0)))

        text = Fonts.burbank.render(f"Score: {self.score}", True, "#ffffff")
        self.WINDOW.blit(text, (self.w(40) + self.X_START, self.h(67)))

        if self.debug:
            self.space.debug_draw(self.DRAW_OPTIONS)

    def draw_game_over(self):
        self.WINDOW.blit(Images.game_over, (self.X_START, 0))

        size = Fonts.burbank.size(f"Highest score: {self.highest_score}")

        x_offset = self.w(self.X_START + 856) - size[0] / 2
        y_offset = self.h(675)

        score_text = Fonts.burbank.render(f"Score: {self.score}", True, "#ff6200")
        self.WINDOW.blit(score_text, (x_offset, y_offset))

        y_offset += size[1] + 10

        highest_score_text = Fonts.burbank.render(
            f"Highest score: {self.highest_score}", True, "#ff6200"
        )
        self.WINDOW.blit(highest_score_text, (x_offset, y_offset))

    def draw(self):
        self.WINDOW.fill((124, 195, 2, 100))
        screens = {"game": self.draw_game, "game over": self.draw_game_over}

        screens[self.screen]()

        pygame.display.update()
