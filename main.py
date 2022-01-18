import pygame

from game import Game

pygame.init()
clock = pygame.time.Clock()
pygame.mixer.set_num_channels(1000)

game = Game()
while True:
    clock.tick(60)
    if game.run_frame() == "quit":
        break
