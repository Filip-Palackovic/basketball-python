import pygame
from game import Game


def run():
    clock = pygame.time.Clock()
    pygame.display.set_caption("Basketball Game: Jevi")

    game = Game()
    game.debug = False
    game.create_boundaries()
    game.load_music()

    match = game.match

    while game.run:
        if game.screen == "game" and match.ball is None:
            game.create_ball()

        game.x_mouse, game.y_mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                ball_velocity_y = -8
                ball_velocity_x = 2  # Set horizontal velocity on click

            ball_velocity_y += 8
            ball
            ball_rect.y += ball_velocity_y
            ball_rect.x += ball_velocity_x  # Move ball horizontally

        #game.handle_events()

        if game.screen == "game" and match.ball is None:
            game.create_ball()

        game.handle_ball_launch()

        game.count_score()

        game.handle_screens()

        game.draw()
        game.space.step(game.DT)
        clock.tick(game.FPS)

    pygame.quit()
    quit()


if __name__ == "__main__":
    run()
