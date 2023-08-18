from math import sin

import pygame


class Entity(pygame.sprite.Sprite):
    def __init__(self, groups) -> None:
        super().__init__(groups)
        self.frame_index = 0
        self.animation_speed = 0.15
        self.direction = pygame.math.Vector2(0, 0)

        self.can_be_hit = True
        self.hit_cooldown = 400
        self.hit_time = None

    def collide(self, direction):
        if direction == "horizontal":
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(
                    self.hitbox
                ):  # pokud se čtverec hráče dotýká čtverce spritu
                    if (
                        self.direction.x > 0
                    ):  # pokud se hráč dotýká spritu zprava, posuneme ho doleva
                        self.hitbox.right = sprite.hitbox.left
                    if (
                        self.direction.x < 0
                    ):  # pokud se hráč dotýká spritu zleva, posuneme ho doprava
                        self.hitbox.left = sprite.hitbox.right
        if direction == "vertical":
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(
                    self.hitbox
                ):  # pokud se čtverec hráče dotýká čtverce spritu
                    if (
                        self.direction.y > 0
                    ):  # hráč se pohybuje dolu, kolize bude zhora
                        self.hitbox.bottom = sprite.hitbox.top
                    if (
                        self.direction.y < 0
                    ):  # hráč se pohybuje nahoru, kolize bude zdola
                        self.hitbox.top = sprite.hitbox.bottom

    def move(self, speed):
        """Pohyb hráče"""
        # potřebujeme normalizovat vstup, jinak do dvou směrů bude hráč rychlejší (trigonometrie)
        if self.direction.length() > 0:  # pokud je vektor nenulový
            self.direction.normalize()  # normalizace vektoru na jedničky
        self.hitbox.x += self.direction.x * speed
        self.collide("horizontal")
        self.hitbox.y += self.direction.y * speed
        self.collide("vertical")
        self.rect.center = self.hitbox.center

    def wave(self):
        """Sinusovka pro alpha"""
        val = sin(pygame.time.get_ticks())
        if val < 0:
            val = 0
        else:
            val = 255
        return val
