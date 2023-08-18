from random import randint

import pygame

from helpers.settings import *


class MagicPlayer:
    def __init__(self, animation_player) -> None:
        self.animation_player = animation_player

    def heal(self, player, strength, cost, groups):
        if player.energy >= cost:
            player.energy -= cost
            player.health += strength
            if player.health >= player.stats["health"]:
                player.health = player.stats["health"]
            self.animation_player.create_particles(
                "heal",
                player.rect.center + pygame.math.Vector2(0, -50),
                groups,
            )
            self.animation_player.create_particles(
                "aura", player.rect.center, groups
            )

    def fireball(self, player, strength, cost, groups):
        print("fireball")
        if player.energy >= cost:
            player.energy -= cost
            direction_dict = {
                "right": pygame.math.Vector2(1, 0),
                "left": pygame.math.Vector2(-1, 0),
                "up": pygame.math.Vector2(0, -1),
                "down": pygame.math.Vector2(0, 1),
            }
            direction = direction_dict[player.status.split("_")[0]]
            for i in range(1, 6):
                randomness = randint(-TILESIZE // 3, TILESIZE // 3)
                if direction.x != 0:
                    offset_x = TILESIZE * i * direction.x
                    self.animation_player.create_particles(
                        "flame",
                        player.rect.center
                        + pygame.math.Vector2(
                            offset_x + randomness, randomness
                        ),
                        groups,
                    )
                else:
                    offset_y = TILESIZE * i * direction.y
                    self.animation_player.create_particles(
                        "flame",
                        player.rect.center
                        + pygame.math.Vector2(
                            randomness, offset_y + randomness
                        ),
                        groups,
                    )
