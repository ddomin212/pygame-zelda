from csv import reader
from os import listdir, walk

import pygame


def import_tilemap_csv(path):
    with open(path) as csvfile:
        return list(reader(csvfile, delimiter=","))


def import_folder(path):
    all = []
    for _, _, data in walk(path):
        all += [
            pygame.image.load(path + "/" + item).convert_alpha()
            for item in data
        ]
    return all


def import_enemy_assets(name):
    enemy_path = "../graphics/monsters/"
    animations = {
        "idle": [],
        "move": [],
        "attack": [],
    }

    main = f"{enemy_path}{name}/"
    for animation in animations.keys():
        animations[animation] = import_folder(main + animation)

    return animations


def import_player_assets():
    character_path = "../graphics/player/"
    animations = {
        "up": [],
        "down": [],
        "left": [],
        "right": [],
        "up_attack": [],
        "down_attack": [],
        "left_attack": [],
        "right_attack": [],
        "up_idle": [],
        "down_idle": [],
        "left_idle": [],
        "right_idle": [],
    }

    for animation in animations.keys():
        files = listdir(character_path + animation)
        for filename in files:
            animations[animation].append(
                pygame.image.load(
                    character_path + animation + "/" + filename
                ).convert_alpha()
            )
    return animations


# print(import_tilemap_csv("../map/map_FloorBlocks.csv"))
