import math
import os
import random

import pygame

pygame.init()
clock = pygame.time.Clock()
running = True


def acceleration_speed(distance):
    if distance / 200 > (math.pi / 2):
        return 60
    else:
        return int(math.sin(distance / 200) * 30)


def distance_from_target(at, to):
    return abs(to - at)


def breaking_length_down(velocity):
    return sum(range(abs(velocity)))


def breaking_length_up(velocity):
    return sum(range(abs(velocity)))


def rot_center(image, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    return rotated_image


def enemy_type_span(score, from_score, to_score, infinite_score=False):
    if infinite_score and (to_score - from_score) / 2 + from_score <= score:
        return 1.
    if from_score <= score < to_score:
        return math.sin((score - from_score) / (to_score - from_score) * math.pi)
    return 0


def movement_direction(at, to, velocity):
    if to > at:
        if velocity < 0 or distance_from_target(at, to) - 7 >= breaking_length_down(velocity):
            return acceleration_speed(distance_from_target(at, to))
        elif velocity > 0:
            return -2
    elif to < at:
        if velocity > 0 or distance_from_target(at, to) - 7 >= breaking_length_up(velocity):
            return -acceleration_speed(distance_from_target(at, to))
        elif velocity < 0:
            return 2
    return 0


class Shot:
    def __init__(self, x, y, direction, owner, damage=10, shot_speed=5):
        self.x = x
        self.y = y
        self.direction = direction
        self.aliveFor = 0
        self.inactive = False
        self.damage = damage
        self.shot_speed = shot_speed
        self.owner = owner

        pygame.mixer.music.load(f'sounds/shot_{random.randint(0, 5) + 1}.mp3')
        pygame.mixer.music.play()

    def move(self):
        self.x += math.cos(math.radians(self.direction)) * self.shot_speed
        self.y += math.sin(math.radians(self.direction)) * self.shot_speed
        self.aliveFor += 1

    def draw(self, screen):
        if not self.inactive:
            if self.owner == "player":
                pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, 2, 8))
            else:
                pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, 2, 8))

    def collision(self, other_x, other_y, other_w, other_h):
        if self.aliveFor > 15 and not self.inactive:
            if other_x < self.x < other_x + other_w and other_y < self.y < other_y + other_h:
                return True
            return False

    def delete(self):
        del self


class Enemy:
    def __init__(self, x, y, direction, image_name, score, health=10, speed=1., random_direction_shift_after=0,
                 direction_shift_by=0, laser_damage=0, laser_speed=0, laser_frequency=0, laser_navigation=False,
                 game_obj=None):
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
                                  "enemy", self.laser_damage))
            else:
                shots.append(Shot(self.x + 32, self.y + 64, self.direction, "enemy", damage=self.laser_damage))

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
        pygame.mixer.music.load(f'sounds/explosion_{random.randint(0, 4) + 1}.mp3')
        pygame.mixer.music.play()


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
        self.lives = 3
        self.pause_game = False

    def run_frame(self):
        for e in pygame.event.get():
            if e.type == pygame.MOUSEMOTION:
                (mouseX, mouseY) = pygame.mouse.get_pos()
                self.set_to_x(mouseX)
                self.set_to_y(mouseY)
            if e.type == pygame.MOUSEBUTTONDOWN:
                self.shoot()
            if e.type == pygame.KEYDOWN:
                self.shoot()
            if e.type == pygame.QUIT:
                global running
                running = False

        if self.pause_game:
            return

        self.handle_movement()
        self.display.fill((0, 0, 0))

        self.display.blit(pygame.transform.scale(self.ship, (64, 64)), (self.__at_x - 32, self.__at_y - 32))
        # theta = math.atan2(self.__to_y - self.__at_y, self.__to_x - self.__at_x)
        # self.display.blit(rot_center(pygame.transform.scale(self.ship, (64, 64)), 270 - math.degrees(theta)),
        #                   (self.__at_x - 32, self.__at_y - 32))

        if random.random() < enemy_type_span(self.score, -60, 440) / 50:
            self.enemies.append(
                Enemy(random.randint(0, 400 - 64), -64, 90, 'enemy_easy.png', 5, 10, 2. + random.random() * .5))

        if random.random() < enemy_type_span(self.score, 100, 560) / 50:
            self.enemies.append(
                Enemy(random.randint(0, 400 - 64), -64, 90, 'enemy_medium.png', 5, 20, 3. + random.random() * 2))

        if random.random() < enemy_type_span(self.score, 480, 1230, True) / 260:
            self.enemies.append(
                Enemy(random.randint(0, 400 - 64), -64, 90, 'enemy_medium.png', 5, 20, 3. + random.random() * 2))

        if random.random() < enemy_type_span(self.score, 300, 900) / 50:
            self.enemies.append(
                Enemy(random.randint(0, 400 - 64), -64, 90, 'enemy_shooter_1.png', 6, 10, 1.4 + random.random() * .3,
                      laser_frequency=100, laser_speed=7, laser_damage=5))

        if random.random() < enemy_type_span(self.score, 800, 1400, True) / 100:
            self.enemies.append(
                Enemy(random.randint(0, 400 - 64), -64, 90, 'enemy_shooter_1.png', 6, 10, 1.4 + random.random() * .3,
                      laser_frequency=100, laser_speed=7, laser_damage=5))

        if random.random() < enemy_type_span(self.score, 450, 1600, True) / 300:
            self.enemies.append(
                Enemy(random.randint(0, 400 - 64), -64, 90, 'enemy_difficult.png', 8, 30, 2. + random.random() * .1,
                      direction_shift_by=4, random_direction_shift_after=2))

        if random.random() < enemy_type_span(self.score, 400, 2400, True) / 150:
            self.enemies.append(
                Enemy(random.randint(0, 400 - 64), -64, 90, 'enemy_shooter_2.png', 10, 20, 1.9 + random.random() * .1,
                      laser_frequency=100, laser_speed=12, laser_damage=5, laser_navigation=True,
                      game_obj=self))

        for shot in self.__shots:
            shot.move()
            shot.draw(self.display)
            if shot.x > 400 or shot.x < 0 or shot.y > 800 or shot.y < 0:
                shot.delete()
                self.__shots.remove(shot)

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

        if self.lives <= 0:
            self.display_defeat()
            self.pause_game = True

        self.ship_collision_with_shot()
        self.display_score()
        self.display_lives()

        pygame.display.flip()

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
            self.__shots.append(Shot(self.__at_x - 14, self.__at_y, self.theta, "player", shot_speed=self.shot_speed))
        elif not self.__shotCannonLeft:
            self.__shots.append(Shot(self.__at_x + 14, self.__at_y, self.theta, "player", shot_speed=self.shot_speed))
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


game = Game()
while running:
    clock.tick(60)
    game.run_frame()
