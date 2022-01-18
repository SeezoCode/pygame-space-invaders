import sys

import pygame

from game import Game

pygame.init()
clock = pygame.time.Clock()

if len(sys.argv) == 2:
    if len(sys.argv) == 2:
        if sys.argv[1] == "sound" or sys.argv[1] == "sounds":
            pygame.mixer.set_num_channels(1000)


game = Game()
while True:
    clock.tick(60)
    if game.run_frame() == "quit":
        break
