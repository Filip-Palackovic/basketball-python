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
    counter = 10
    jumpt = False

    def __init__(self) -> None:
        self.run = True
        self.debug = False

        self.space = pymunk.Space()
        self.space.gravity = (0, 981)
        self.angle: int = 0
        self.mouse_distance: int = 0
        self.mouse_pressed: bool = False
        self.time_bar_color = (255, 0, 0)

        self.SPACE_pressed: bool = False
        self.ball_velocity_y: int = 0
        self.ball_velocity_x: int = 0
        self.ball_recty: int = 0
        self.ball_rectx: int = 0

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


    def create_ball(self):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = 0,0
        shape = pymunk.Circle(body, self.w(30), (0, 0))
        shape.mass = 10
        shape.color = (255, 0, 0, 100)
        shape.elasticity = 0.9
        shape.friction = 1
        self.space.add(body, shape)
        self.match.ball = shape



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
        self.SPACE_pressed = False
        if (event.type == pygame.QUIT) or (event.type == KEYDOWN and event.key == K_F4):
            self.run = False
        if event.type == KEYDOWN:
            if event.key == K_p:
                self.r_disabled = not self.r_disabled
            if event.key == K_r and not self.r_disabled:
                self.match.restart()
            if event.key == K_SPACE:
                self.SPACE_pressed = True
                self.handle_ball_launch()
                
            elif event.key == K_t:
                self.update_highest_score()
                self.screen = "game over"

    def handle_mouse_events(self, event: pygame.event.Event): # Maus gedrückt ? 
        if (
                self.match.start_time + 0.5 > time.time()
            ):  # Avoids the ball from being launched when clicking the restart button.
            return
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

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.match.clicked = True  # Reset the clicked attribute


    def handle_ball_launch(self):
            if (
                self.match.start_time + 0.5 > time.time() and self.run == True
            ):  # Avoids the ball from being launched when clicking the restart button.
                self.ball_velocity_y=0
                self.ball_velocity_x = 0
                self.ball_recty=0
                self.ball_rectx=0
                return
    
            if self.SPACE_pressed:
                self.ball_velocity_y = -7
                self.ball_velocity_x = 3
                
            self.ball_velocity_y += 0.2
            self.ball_recty += self.ball_velocity_y
            self.ball_rectx += self.ball_velocity_x
            
            self.match.ball.body.position = self.ball_rectx, self.ball_recty    

            pos = convert_to_pygame(self.match.ball.body.position)
            ball_rect = pygame.Rect(*pos, *Images.ball.get_size())

            

            EndBorder = pygame.Rect(self.X_END + self.w(50), self.h(0 - 50),self.w(100), self.h(self.FLOOR_HEIGHT+50))
            if ball_rect.colliderect(EndBorder):
                self.ball_rectx = 0
                self.match.ball.body.position = 0,self.ball_recty 

            HoopBorder = pygame.Rect(self.w(1464 + self.X_START), self.h(265),self.w(10), self.h(10))
            HoopBorder2 = pygame.Rect(self.w(1600 + self.X_START), self.h(265),self.w(7), self.h(10))
            BackbordBorder = pygame.Rect(self.w((1600 + 1654) / 2 + self.X_START), self.h(70),self.w(26), self.h(350))
            Net1 = pygame.Rect(self.w(1471 + 36 / 2 + self.X_START), self.h(274 + 140 / 2),self.w(5), self.h(70))
            Net2 = pygame.Rect(self.w(self.X_START + 1585 + 33 / 2), self.h(339.5),self.w(5), self.h(70))
            if ball_rect.colliderect(BackbordBorder) or ball_rect.colliderect(HoopBorder) or ball_rect.colliderect(Net1) or ball_rect.colliderect(Net2):
                self.ball_velocity_y = 5
                self.ball_velocity_x = -5

            if ball_rect.colliderect(HoopBorder2):
                self.ball_velocity_y = -3
                self.ball_velocity_x = -2

            Goal = pygame.Rect(self.w(1500 + self.X_START), self.h(300),self.w(80), self.h(6))
            if ball_rect.colliderect(Goal):
                if self.score < 5:
                    self.match.remaining_time = time.time() + 15
                elif self.score < 10:
                    self.match.remaining_time = time.time() + 10
                else:
                    self.match.remaining_time = time.time() + 7
                self.score += 1
                self.ball_velocity_y = 0
                self.ball_velocity_x = 3
                self.ball_rectx = 0
                self.match.ball.body.position = 0,self.ball_recty 
                

            self.match.ball.body.body_type = pymunk.Body.DYNAMIC

            
    def draw_game(self):
        self.WINDOW.blit(Images.background, (self.X_START, 0))

        if self.match.ball:
            pos = convert_to_pygame(self.match.ball.body.position)
            image = rot_center(Images.ball, 0)
            self.WINDOW.blit(image, pos)

        self.WINDOW.blit(Images.net, (self.w(1445 + self.X_START), self.h(0)))

        self.WINDOW.blit(Images.basket, (self.w(1445 + self.X_START), self.h(0)))

        text = Fonts.burbank.render(f"Score: {self.score}", True, "#ffffff")
        self.WINDOW.blit(text, (self.w(40) + self.X_START, self.h(67)))

        if isinstance(self.match.remaining_time, float):
            time_remaining = int(max(0, self.match.remaining_time - time.time()))+1
            time_text = Fonts.burbank.render(f"Time: {time_remaining} seconds", True, "#ffffff")
            self.WINDOW.blit(time_text, (self.w(40) + self.X_START, self.h(300)))


            time_bar_width = self.w(500)
            time_bar_height = self.h(20)
            time_bar_x = self.w(500) + self.X_START
            time_bar_y = self.h(100)

            bar_width = self.w(800)
            bar_height = self.h(70)
            bar_x = self.w(475) + self.X_START
            bar_y = self.h(75)

            remaining_ratio = time_remaining/10
            remaining_width = time_bar_width * remaining_ratio

            pygame.draw.rect(
                self.WINDOW,
                (105,105,105),
                (bar_x, bar_y, bar_width, bar_height),
            )

            pygame.draw.rect(
                self.WINDOW,
                self.time_bar_color,
                (time_bar_x, time_bar_y, remaining_width, time_bar_height),
            )

          
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