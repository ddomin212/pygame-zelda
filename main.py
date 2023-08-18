import sys

import pygame

from helpers.settings import *
from world.level import Level


class Game:
    def __init__(self):
        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        pygame.display.set_caption("Zelda")
        self.clock = pygame.time.Clock()

        self.level = Level()  # definujeme naší úroveň

    def run(self):
        while True:  # hlavní smyčka hry
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.level.toggle()

            self.screen.fill(WATER_COLOR)
            self.level.run()  # načteme úroveň
            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.run()
