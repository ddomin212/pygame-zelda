import os

import pygame

from debug import debug
from entities.entity import Entity
from helpers.settings import *
from helpers.utils import import_player_assets


class Player(Entity):
    def __init__(
        self,
        pos,
        groups,
        obstacle_sprites,
        create_attack,
        destroy_weapon,
        create_magic,
    ):
        super().__init__(groups)
        self.image = pygame.image.load(
            "../graphics/test/player.png"
        ).convert_alpha()  # obrázek pro hráče
        self.rect = self.image.get_rect(topleft=pos)  # bounding box hráče
        self.hitbox = self.rect.inflate(-6, HITBOX_OFFSET["player"])

        self.animations = import_player_assets()
        self.status = "down"

        self.create_magic = create_magic
        self.magic_index = 0
        self.magic = list(magic_data.keys())[self.magic_index]
        self.can_magic_switch = True
        self.magic_time = None

        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None

        self.obstacle_sprites = obstacle_sprites

        self.create_attack = create_attack
        self.destroy_weapon = destroy_weapon
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_weapon_switch = True
        self.weapon_time = None
        self.weapon_cooldown = 200

        self.stats = {
            "health": 100,
            "energy": 60,
            "attack": 10,
            "magic": 4,
            "speed": 5,
        }
        self.upgrade_cost = {
            "health": 100,
            "energy": 100,
            "attack": 100,
            "magic": 100,
            "speed": 100,
        }
        self.max_stats = {
            "health": 300,
            "energy": 140,
            "attack": 20,
            "magic": 10,
            "speed": 10,
        }
        self.exp = 10000
        self.health = self.stats["health"]
        self.energy = self.stats["energy"]
        self.speed = self.stats["speed"]

    def get_status(self):
        status = self.status.split("_")[0]
        if (
            self.direction.x == 0
            and self.direction.y == 0
            and "_idle" not in self.status
        ):
            self.status = status + "_idle"

        if self.attacking and "_attack" not in self.status:
            self.direction = pygame.math.Vector2(0, 0)
            self.status = status + "_attack"

    def get_attack_damage(self):
        return self.stats["attack"] + weapon_data[self.weapon]["damage"]

    def get_magic_damage(self):
        return self.stats["magic"] + magic_data[self.magic]["strength"]

    def get_value_by_index(self, index):
        return list(self.stats.values())[index]

    def get_cost_by_index(self, index):
        return list(self.upgrade_cost.values())[index]

    def input(self):
        """Zpracování vstupu hráče"""
        keys = pygame.key.get_pressed()

        # movement input

        if keys[pygame.K_w]:
            self.direction.y = -1
            self.status = "up"
        elif keys[pygame.K_s]:
            self.direction.y = 1
            self.status = "down"
        else:
            self.direction.y = 0

        if keys[pygame.K_a]:
            self.direction.x = -1
            self.status = "left"
        elif keys[pygame.K_d]:
            self.direction.x = 1
            self.status = "right"
        else:
            self.direction.x = 0

        # attack input
        if keys[pygame.K_SPACE]:
            self.attacking = True
            self.create_attack()

        # magic
        if keys[pygame.K_r]:
            self.attacking = True
            data = magic_data[self.magic]
            strength, cost = (
                data["strength"] + self.stats["magic"],
                data["cost"],
            )  # crashes, needs fix
            self.create_magic(self.magic, strength, cost)

        if keys[pygame.K_q] and self.can_weapon_switch:
            self.can_weapon_switch = False
            if self.weapon_index < len(list(weapon_data.keys())) - 1:
                self.weapon_index += 1
            else:
                self.weapon_index = 0
            self.weapon = list(weapon_data.keys())[self.weapon_index]

        if keys[pygame.K_e] and self.can_magic_switch:
            self.can_magic_switch = False
            if self.magic_index < len(list(magic_data.keys())) - 1:
                self.magic_index += 1
            else:
                self.magic_index = 0
            self.magic = list(magic_data.keys())[self.magic_index]

    def cooldown(self):
        """Cooldown pro útoky"""
        if self.attacking:
            if self.attack_time is None:
                self.attack_time = pygame.time.get_ticks()
            if (
                pygame.time.get_ticks() - self.attack_time
                > self.attack_cooldown + weapon_data[self.weapon]["cooldown"]
            ):
                self.attacking = False
                self.attack_time = None
                self.destroy_weapon()

        if self.can_weapon_switch is False:
            if self.weapon_time is None:
                self.weapon_time = pygame.time.get_ticks()
            if (
                pygame.time.get_ticks() - self.weapon_time
                > self.weapon_cooldown
            ):
                self.can_weapon_switch = True
                self.weapon_time = None

        if self.can_magic_switch is False:
            if self.magic_time is None:
                self.magic_time = pygame.time.get_ticks()
            if (
                pygame.time.get_ticks() - self.magic_time
                > self.weapon_cooldown
            ):
                self.can_magic_switch = True
                self.magic_time = None

        if self.can_be_hit is False:
            if self.hit_time is None:
                self.hit_time = pygame.time.get_ticks()
            if pygame.time.get_ticks() - self.hit_time > self.hit_cooldown:
                self.can_be_hit = True
                self.hit_time = None

    def energy_recovery(self):
        if self.energy < self.stats[
            "energy"
        ] and self.direction == pygame.math.Vector2(0, 0):
            self.energy += 0.01 * self.stats["magic"]
        elif self.energy > self.stats["energy"]:
            self.energy = self.stats["energy"]

    def animate(self):
        animation = self.animations[self.status]

        # loop skrze frames
        self.frame_index += self.animation_speed

        if self.frame_index >= len(animation):
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(
            center=self.hitbox.center
        )  # musíme aktualizovat i rect, protože se mění velikost obrázku z animace na animaci

        if self.can_be_hit is False:
            alpha = self.wave()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def update(self):
        """Aktualizace hráče vzhledem k toku hry"""
        if not self.attacking:
            self.input()
        self.cooldown()
        self.get_status()
        self.animate()
        self.move(self.stats["speed"])
        self.energy_recovery()
