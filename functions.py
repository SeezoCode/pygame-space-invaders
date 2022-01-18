import math

import pygame


def breaking_length_down(velocity):
    return sum(range(abs(velocity)))


def acceleration_speed(distance):
    if distance / 200 > (math.pi / 2):
        return 60
    else:
        return int(math.sin(distance / 200) * 30)


def distance_from_target(at, to):
    return abs(to - at)


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