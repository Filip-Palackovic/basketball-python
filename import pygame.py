import pygame
import sys
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

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 400
FPS = 60
GRAVITY = 0.25
FLAP_STRENGTH = -8
HOOP_POSITION = (500, 150)
BALL_RADIUS = 20
HOOP_SIZE = (80, 60)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Basketball Hoop Game")
clock = pygame.time.Clock()

# bild
ball_img = pygame.image.load('ball.png')  
# ball 
ball_rect = ball_img.get_rect()
ball_rect.center = (WIDTH // 4, HEIGHT // 2)
ball_velocity_y = 0
ball_velocity_x = 0  # velocity in x-richtung

# korb
hoop_rect = pygame.Rect(HOOP_POSITION, HOOP_SIZE)


running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            ball_velocity_y = FLAP_STRENGTH
            ball_velocity_x = 2  #  horizontal velocity mit click

    ball_velocity_y += GRAVITY
    ball_rect.y += ball_velocity_y
    ball_rect.x += ball_velocity_x  # Ball horizontal

    # Kollision mt Korb noch ändern
    if ball_rect.colliderect(hoop_rect):
        print("Golaso!")
        ball_rect.y = 150
        ball_rect.x = 150
        

    
    screen.blit(ball_img, ball_rect)
    pygame.draw.rect(screen, WHITE, hoop_rect)

    pygame.display.flip()
    clock.tick(FPS)