import math
import random
import sys

import pygame


class Shot:
    def __init__(self, x, y, direction, owner, damage=10, shot_speed=5, x_momentum=0., y_momentum=0.):
        self.x = x
        self.y = y
        self.direction = direction
        self.aliveFor = 0
        self.inactive = False
        self.damage = damage
        self.shot_speed = shot_speed
        self.owner = owner

        # if abs(x_momentum) > 2:
        #     x_momentum = x_momentum - (x_momentum / abs(x_momentum)) * (abs(x_momentum) - 2)
        y_momentum *= 1
        if x_momentum:
            self.x_momentum = (x_momentum / abs(x_momentum)) * math.pow(abs(x_momentum), 1/4)
        else:
            self.x_momentum = 0
        self.y_momentum = y_momentum

        if len(sys.argv) == 2:
            if sys.argv[1] == "sound" or sys.argv[1] == "sounds":
                pygame.mixer.Channel(random.randint(0, 999)).play(
                    pygame.mixer.Sound(f'sounds/shot_1.mp3'))

    def move(self):
        self.x += math.cos(math.radians(self.direction)) * self.shot_speed + self.x_momentum
        self.y += math.sin(math.radians(self.direction)) * self.shot_speed + self.y_momentum
        if self.x_momentum > 0:
            self.x_momentum -= .1
        elif self.x_momentum < 0:
            self.x_momentum += .1
        if self.y_momentum > 0:
            self.y_momentum -= .1
        elif self.y_momentum < 0:
            self.y_momentum += .1
        self.aliveFor += 1

    def draw(self, screen):
        if not self.inactive:
            if self.owner == "player":
                pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, 2, 8))
            else:
                pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, 2, 8))

    def collision(self, other_x, other_y, other_w, other_h):
        if self.aliveFor < 15 and self.owner == 'enemy':
            return
        if not self.inactive:
            if other_x < self.x < other_x + other_w and other_y < self.y < other_y + other_h:
                return True
            return False

    def delete(self):
        del self