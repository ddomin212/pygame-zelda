from typing import Any

import pygame

from entities.entity import Entity
from helpers.settings import *
from helpers.utils import import_enemy_assets


class Enemy(Entity):
    def __init__(
        self,
        monster_name,
        pos,
        groups,
        obstacle_sprites,
        damage_player,
        particle_func,
        enemy_xp,
    ) -> None:
        super().__init__(groups)
        self.sprite_type = "enemy"

        self.animations = import_enemy_assets(monster_name)
        # print(self.animations)
        self.status = "idle"
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)
        self.obstacle_sprites = obstacle_sprites

        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        self.health = monster_info["health"]
        self.exp = monster_info["exp"]
        self.speed = monster_info["speed"]
        self.attack_damage = monster_info["damage"]
        self.resistance = monster_info["resistance"]
        self.attack_radius = monster_info["attack_radius"]
        self.notice_radius = monster_info["notice_radius"]
        self.attack_type = monster_info["attack_type"]

        self.can_attack = True
        self.attack_cooldown = 400
        self.attack_time = None
        self.damage_player = damage_player
        self.particle_func = particle_func
        self.enemy_xp = enemy_xp

    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()
        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2(0, 0)

        return distance, direction

    def get_status(self, player):
        distance, _ = self.get_player_distance_direction(player)

        if distance <= self.attack_radius and self.can_attack:
            if (
                self.status != "attack"
            ):  # chceme prerusit kazdou animaci utokem
                self.frame_index = 0
            self.status = "attack"
        elif distance <= self.notice_radius:
            self.status = "move"
        else:
            self.status = "idle"

    def get_damage(self, player, attack_type):
        if self.can_be_hit:
            self.direction = self.get_player_distance_direction(player)[
                1
            ]  # we have to know the direction to knockback the enemy to the other side
            if attack_type == "weapon":
                damage = player.get_attack_damage()
            elif attack_type == "magic":
                damage = player.get_magic_damage()
            else:
                damage = 0
            self.health -= damage
            self.can_be_hit = False
            self.hit_time = pygame.time.get_ticks()

    def destroy_self(self):
        if self.health <= 0:
            self.kill()
            self.enemy_xp(self.exp)
            self.particle_func(self.rect.center, self.monster_name)

    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.animations[self.status]):
            if self.status == "attack":
                self.can_attack = False
            self.frame_index = 0
        self.image = self.animations[self.status][int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        if self.can_be_hit is False:
            alpha = self.wave()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def hit_reaction(self):
        if not self.can_be_hit:
            self.direction *= (
                -self.resistance / 2
            )  # odrazi se od hrace o resistance

    def actions(self, player):
        if self.status == "attack":
            self.damage_player(self.attack_damage, self.attack_type)
        elif self.status == "move":
            self.direction = self.get_player_distance_direction(player)[1]
        else:
            self.direction = pygame.math.Vector2()

    def cooldown(self):
        if self.can_attack is False:
            if self.attack_time is None:
                self.attack_time = pygame.time.get_ticks()
            if (
                pygame.time.get_ticks() - self.attack_time
                > self.attack_cooldown
            ):
                self.can_attack = True
                self.attack_time = None

        if self.can_be_hit is False:
            if self.hit_time is None:
                self.hit_time = pygame.time.get_ticks()
            if pygame.time.get_ticks() - self.hit_time > self.hit_cooldown:
                self.can_be_hit = True
                self.hit_time = None

    def update(self) -> None:
        self.hit_reaction()
        self.move(self.speed)
        self.animate()
        self.cooldown()
        self.destroy_self()

    def enemy_update(self, player) -> None:  # jenom pro enemy kvuli vykonnosti
        self.get_status(player)
        self.actions(player)
