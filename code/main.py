# import everything from settings
import pygame
import os
from settings import *
from pytmx.util_pygame import load_pygame


# game class
class Game:
    def __init__(self):
        # initialize all pygame modules
        pygame.init()
        # create main game window
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        # set title of the window
        pygame.display.set_caption('Verdentia')

        self.import_assets()

    def import_assets(self):
        base_path = os.path.dirname(os.path.abspath(__file__))  # path to code
        map_path = os.path.join(base_path, '..', 'data', 'maps', 'world.tmx')
        self.tmx_maps = {'world': load_pygame(map_path)}

    def run(self):
        # main game loop to keep the game running
        while True:
            # game loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # if the user clicks the close button
                    pygame.quit()
                    exit()
            # update the display with any changes
            pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()

