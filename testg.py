import pygame
from pygame.locals import QUIT
import pymunk
from pymunk.vec2d import Vec2d

# Initialize Pygame
pygame.init()

# Pygame screen settings
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Basketball Jump Shot")

# Pymunk space setup
space = pymunk.Space()
space.gravity = 0, -900  # Set the gravity, adjust as needed

# Ball setup
mass = 1
radius = 20
moment = pymunk.moment_for_circle(mass, 0, radius)
ball_body = pymunk.Body(mass, moment)
ball_shape = pymunk.Circle(ball_body, radius)
ball_shape.elasticity = 0.8  # Bounciness

# Initial position of the ball
ball_body.position = width // 2, height // 2
space.add(ball_body, ball_shape)

# Pygame clock to control the frame rate
clock = pygame.time.Clock()

# Main game loop
running = True
jumping = False
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not jumping:
            # Apply impulse for the jump when the spacebar is pressed
            ball_body.apply_impulse_at_local_point(Vec2d(0, 5000))
            jumping = True

    # Clear the screen
    screen.fill((255, 255, 255))

    # Step the Pymunk space
    space.step(1 / 60.0)

    # Draw the ball
    pygame.draw.circle(screen, (0, 0, 255), (int(ball_body.position.x), int(height - ball_body.position.y)), radius)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Clean up when the game loop exits
pygame.quit()