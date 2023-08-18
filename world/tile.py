import pygame

from helpers.settings import *


class Tile(pygame.sprite.Sprite):
    def __init__(
        self,
        pos,
        groups,
        sprite_type,
        surface=pygame.Surface((TILESIZE, TILESIZE)),
    ):
        super().__init__(groups)
        self.image = surface
        self.sprite_type = sprite_type  # typ spritu, enemák, předmět, atd.
        y_offset = HITBOX_OFFSET[self.sprite_type]
        if sprite_type == "object":
            self.rect = self.image.get_rect(
                topleft=(pos[0], pos[1] - TILESIZE)
            )
        else:
            self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(
            0, y_offset
        )  # hitbox je o X px menší než sprite, aby se hráč mohl overlapovat s tilem
