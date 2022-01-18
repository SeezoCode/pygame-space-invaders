import math
import os
import random
import sys

import pygame

from functions import rot_center
from shot import Shot


class Enemy:
    def __init__(self, x, y, direction, image_name, score, health=10, speed=1., random_direction_shift_after=0,
                 direction_shift_by=0, laser_damage=0, laser_speed=0, laser_frequency=0, laser_navigation=False,
                 game_obj=None, property_list=None):
        self.x = x
        self.y = y
        self.direction = direction
        self.aliveFor = 0
        self.inactive = False
        self.image = pygame.image.load(os.path.join("data", image_name))
        self.speed = speed
        self.health = health
        self.score = score
        self.random_direction_shift_after = random_direction_shift_after
        self.direction_shift_by = direction_shift_by
        self.laser_damage = laser_damage
        self.laser_speed = laser_speed
        self.laser_frequency = laser_frequency
        self.momentum = 0
        self.laser_navigation = laser_navigation
        self.property_list = property_list
        if game_obj is not None:
            self.game = game_obj

    def move(self, shots):
        self.x += math.cos(math.radians(self.direction)) * self.speed
        self.y += math.sin(math.radians(self.direction)) * self.speed
        self.aliveFor += 1

        for shot in shots:
            if shot.collision(self.x, self.y, 64, 64):
                self.health -= shot.damage
                shot.inactive = True
        if self.random_direction_shift_after and self.aliveFor % self.random_direction_shift_after == 0:
            self.momentum += random.randint(-self.direction_shift_by, self.direction_shift_by)
            if self.x < 0 or self.x > 400 - 64:
                self.momentum = -self.momentum
            if abs(self.momentum) > 4:
                self.momentum = self.momentum - (self.momentum / abs(self.momentum)) * (abs(self.momentum) - 4)
            self.x += self.momentum

        if self.laser_frequency and random.randint(0, self.laser_frequency) == 0:
            if self.laser_navigation and self.game:
                shots.append(Shot(self.x + 32, self.y + 32, self.get_angle(self.game.get_to_x(), self.game.get_to_y()),
                                  "enemy", self.laser_damage, x_momentum=self.momentum, y_momentum=self.speed))
            else:
                shots.append(Shot(self.x + 32, self.y + 64, self.direction, "enemy", damage=self.laser_damage,
                                  x_momentum=self.momentum, y_momentum=self.speed))

    def get_angle(self, player_x, player_y):
        return math.degrees(math.atan2(player_y - self.y, player_x - self.x))

    def draw(self, screen):
        if not self.inactive:
            screen.blit(rot_center(pygame.transform.scale(self.image, (64, 64)), 180), (self.x, self.y))

    def collision(self, other_x, other_y, other_w, other_h):
        if self.aliveFor > 10 and not self.inactive:
            if other_x < self.x < other_x + other_w and other_y < self.y < other_y + other_h:
                return True
        return False

    def delete(self):
        del self
        if len(sys.argv) == 2:
            if sys.argv[1] == "sound" or sys.argv[1] == "sounds":
                pygame.mixer.music.load(f'sounds/explosion_{random.randint(0, 1) + 1}.mp3')
                pygame.mixer.music.play()

