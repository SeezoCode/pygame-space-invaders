import os
import random

import pygame

from functions import enemy_type_span, movement_direction
from shot import Shot
from enemy import Enemy


class Game:
    __to_x = 0
    __to_y = 0
    __at_x = 0
    __at_y = 0
    __v_x = 0
    __v_y = 0
    max_speed = 20.0
    __shots = []
    __shotCannonLeft = True
    shot_speed = 5
    __held_space_at_time = 0
    __power_ups = []

    def __init__(self):
        self.score = 0
        self.enemies = []
        pygame.init()
        self.running = True
        self.display = pygame.Surface = pygame.display.set_mode((400, 800))
        pygame.display.set_caption("Space Invaders")
        self.round_tick = 0
        self.clock = pygame.time.Clock()
        self.ship = pygame.image.load(os.path.join('data', 'spaceship.png'))
        self.theta = 270
        self.lives = 5
        self.pause_game = False

    def run_frame(self):
        for e in pygame.event.get():
            if e.type == pygame.MOUSEMOTION:
                (mouseX, mouseY) = pygame.mouse.get_pos()
                self.set_to_x(mouseX)
                self.set_to_y(mouseY)
            if e.type == pygame.KEYDOWN:
                self.shoot()
            if e.type == pygame.QUIT:
                return "quit"

        if self.pause_game:
            return

        if pygame.mouse.get_pressed()[0]:
            if self.__held_space_at_time + 120 < pygame.time.get_ticks():
                self.shoot()
                self.__held_space_at_time = pygame.time.get_ticks()

        self.handle_movement()
        self.display.fill((0, 0, 0))

        self.display.blit(pygame.transform.scale(self.ship, (64, 64)), (self.__at_x - 32, self.__at_y - 32))
        # theta = math.atan2(self.__to_y - self.__at_y, self.__to_x - self.__at_x)
        # self.display.blit(rot_center(pygame.transform.scale(self.ship, (64, 64)), 270 - math.degrees(theta)),
        #                   (self.__at_x - 32, self.__at_y - 32))

        difficulty = .5 + self.score / 1000
        self.handle_enemies_addition(difficulty)

        if random.random() < .0001:
            self.__power_ups.append(
                Enemy(random.randint(0, 400 - 64), -64, 90, 'heart.png', 0, 10, 4. + random.random() * 3.,
                      property_list=('health',)))

        self.handle_shot_list()
        self.handle_enemy_list()
        self.handle_power_ups()

        if self.lives <= 0:
            self.display_defeat()
            self.pause_game = True

        self.ship_collision_with_shot()
        self.display_score()
        self.display_lives()
        self.display_difficulty(difficulty)

        pygame.display.flip()

    def handle_enemy_list(self):
        for enemy in self.enemies:
            enemy.move(self.__shots)
            enemy.draw(self.display)
            if enemy.collision(self.__at_x - 64, self.__at_y - 64, 64, 64) or enemy.health <= 0:
                self.score += enemy.score
                enemy.delete()
                self.enemies.remove(enemy)
                if enemy.health > 0:
                    self.lives -= 1
            if enemy.y > 800:
                enemy.delete()
                self.enemies.remove(enemy)
                self.lives -= 1

    def handle_power_ups(self):
        for power_up in self.__power_ups:
            power_up.move(self.__shots)
            power_up.draw(self.display)
            if power_up.collision(self.__at_x - 64, self.__at_y - 64, 64, 64) or power_up.health <= 0:
                power_up.delete()
                self.__power_ups.remove(power_up)
                if 'health' in power_up.property_list:
                    self.lives += 1
            if power_up.y > 800:
                power_up.delete()
                self.__power_ups.remove(power_up)

    def handle_shot_list(self):
        for shot in self.__shots:
            shot.move()
            shot.draw(self.display)
            if shot.x > 400 or shot.x < 0 or shot.y > 800 or shot.y < 0:
                shot.delete()
                self.__shots.remove(shot)

    def handle_enemies_addition(self, difficulty):
        if random.random() < enemy_type_span(self.score, -60, 440) / 30 * difficulty:
            self.enemies.append(
                Enemy(random.randint(0, 400 - 64), -64, 90, 'enemy_easy.png', 5, 10, 2. + random.random() * .5))

        if random.random() < enemy_type_span(self.score, 100, 560) / 50 * difficulty:
            self.enemies.append(
                Enemy(random.randint(0, 400 - 64), -64, 90, 'enemy_medium.png', 5, 10, 3. + random.random() * 2))

        if random.random() < enemy_type_span(self.score, 480, 1230, True) / 260 * difficulty:
            self.enemies.append(
                Enemy(random.randint(0, 400 - 64), -64, 90, 'enemy_medium.png', 5, 10, 2. + random.random() * 2))

        if random.random() < enemy_type_span(self.score, 300, 900) / 80 * difficulty:
            self.enemies.append(
                Enemy(random.randint(0, 400 - 64), -64, 90, 'enemy_shooter_1.png', 6, 10, 1.4 + random.random() * .3,
                      laser_frequency=100, laser_speed=7, laser_damage=5))

        if random.random() < enemy_type_span(self.score, 800, 1400, True) / 200 * difficulty:
            self.enemies.append(
                Enemy(random.randint(0, 400 - 64), -64, 90, 'enemy_shooter_1.png', 6, 10, 1.4 + random.random() * .3,
                      laser_frequency=100, laser_speed=7, laser_damage=5))

        if random.random() < enemy_type_span(self.score, 450, 1600, True) / 240 * difficulty:
            self.enemies.append(
                Enemy(random.randint(0, 400 - 64), -64, 90, 'enemy_difficult.png', 8, 20, 2. + random.random() * .1,
                      direction_shift_by=4, random_direction_shift_after=2))

        if random.random() < enemy_type_span(self.score, 400, 2350, True) / 150 * difficulty:
            self.enemies.append(
                Enemy(random.randint(0, 400 - 64), -64, 90, 'enemy_shooter_2.png', 10, 10, 1.4 + random.random() * .1,
                      laser_frequency=100, laser_speed=12, laser_damage=5, laser_navigation=True,
                      game_obj=self))

    def display_score(self):
        font = pygame.font.SysFont("Arial", 20)
        text = font.render("Score: " + str(self.score), True, (255, 255, 255))
        self.display.blit(text, (0, 0))

    def display_lives(self):
        font = pygame.font.SysFont("Arial", 20)
        text = font.render("Lives: " + str(self.lives), True, (255, 255, 255))
        self.display.blit(text, (0, 20))

    def display_defeat(self):
        font = pygame.font.SysFont("Arial", 40)
        text = font.render(f"You Lose!", True, (255, 255, 255))
        text2 = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.display.blit(text, (110, 200))
        self.display.blit(text2, (110, 250))

    def display_difficulty(self, difficulty):
        font = pygame.font.SysFont("Arial", 20)
        text = font.render("Difficulty: " + str(round(difficulty, 1)), True, (255, 255, 255))
        self.display.blit(text, (0, 40))

    def handle_movement(self):
        self.__v_x += movement_direction(self.__at_x, self.__to_x, self.__v_x)
        self.__v_y += movement_direction(self.__at_y, self.__to_y, self.__v_y)

        self.__at_x += self.__v_x
        self.__at_y += self.__v_y

    def set_to_x(self, x):
        self.__to_x = x

    def get_to_x(self):
        return self.__to_x

    def set_to_y(self, y):
        self.__to_y = y

    def get_to_y(self):
        return self.__to_y

    def shoot(self):
        if self.__shotCannonLeft:
            self.__shots.append(Shot(self.__at_x - 14, self.__at_y, self.theta, "player", shot_speed=self.shot_speed,
                                     x_momentum=self.__v_x, y_momentum=self.__v_y))
        elif not self.__shotCannonLeft:
            self.__shots.append(Shot(self.__at_x + 14, self.__at_y, self.theta, "player", shot_speed=self.shot_speed,
                                     x_momentum=self.__v_x, y_momentum=self.__v_y))
        self.__shotCannonLeft = not self.__shotCannonLeft

    def ship_collision_with_shot(self):
        for shot in self.__shots:
            if shot.collision(self.__at_x - 32, self.__at_y - 32, 64, 64):
                if shot.owner == "player" and shot.aliveFor < 50:
                    return
                self.lives -= 1
                shot.inactive = True
                print(f"Lives: {self.lives}")

    def add_enemy(self, enemy):
        self.enemies.append(enemy)

