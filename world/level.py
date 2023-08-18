from random import randint

import pygame

from attacks.magic import MagicPlayer
from attacks.weapon import Weapon
from debug import debug
from entities.enemy import Enemy
from entities.player import Player
from helpers.settings import *
from helpers.utils import import_folder, import_tilemap_csv
from menus.ui import UI
from menus.upgrade import Upgrade

from .particles import AnimationPlayer
from .tile import Tile


class Level:
    def __init__(self) -> None:
        # potřebujeme náš displej
        self.screen = pygame.display.get_surface()
        self.game_paused = False

        # definujeme si skupiny spriteů
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        self.create_map()  # vytvoříme mapu

        self.ui = UI()
        self.upgrade = Upgrade(self.player)

        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

    def create_attack(self):
        """Vytvoříme útok"""
        self.current_attack = Weapon(
            self.player, [self.visible_sprites, self.attack_sprites]
        )

    def create_magic(self, style, strenght, cost):
        if style == "flame":
            self.magic_player.fireball(
                self.player,
                strenght,
                cost,
                [self.visible_sprites, self.attack_sprites],
            )
        if style == "heal":
            self.magic_player.heal(
                self.player,
                strenght,
                cost,
                [self.visible_sprites],
            )
        self.current_attack = None

    def despawn_weapon(self):
        """Odstraníme útok"""
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def toggle(self):
        self.game_paused = not self.game_paused

    def add_xp(self, xp):
        self.player.exp += xp

    def create_map(self):
        """Vytvoření mapy z 2D pole"""
        layout = {
            "boundary": import_tilemap_csv("../map/map_FloorBlocks.csv"),
            "grass": import_tilemap_csv("../map/map_Grass.csv"),
            "object": import_tilemap_csv("../map/map_LargeObjects.csv"),
            "entities": import_tilemap_csv("../map/map_Entities.csv"),
        }
        graphics = {
            "grass": import_folder("../graphics/grass"),
            "objects": import_folder("../graphics/objects"),
        }
        for style, layout in layout.items():
            for ri, row in enumerate(layout):
                for ci, col in enumerate(row):
                    x, y = ci * TILESIZE, ri * TILESIZE
                    if col != "-1":
                        if style == "boundary":
                            Tile(
                                (x, y),
                                [self.obstacle_sprites],
                                "invisible",
                            )
                        if style == "grass":
                            Tile(
                                (x, y),
                                [
                                    self.visible_sprites,
                                    self.obstacle_sprites,
                                    self.attackable_sprites,
                                ],
                                "grass",
                                graphics["grass"][
                                    randint(0, len(graphics["grass"]) - 1)
                                ],
                            )
                        if style == "object":
                            Tile(
                                (x, y),
                                [self.visible_sprites, self.obstacle_sprites],
                                "object",
                                graphics["objects"][int(col)],
                            )
                        if style == "entities":
                            if col == "394":
                                self.player = Player(
                                    (x, y),
                                    [
                                        self.visible_sprites
                                    ],  # hráč je visible sprite
                                    self.obstacle_sprites,  # hráč NENÍ obstacle sprite, pouze ho potřebujeme pro kolize
                                    self.create_attack,
                                    self.despawn_weapon,
                                    self.create_magic,
                                )
                            else:
                                if col == "390":
                                    monster_name = "bamboo"
                                elif col == "391":
                                    monster_name = "spirit"
                                elif col == "392":
                                    monster_name = "raccoon"
                                else:
                                    monster_name = "squid"
                                Enemy(
                                    monster_name,
                                    (x, y),
                                    [
                                        self.visible_sprites,
                                        self.attackable_sprites,
                                    ],
                                    self.obstacle_sprites,
                                    self.damage_player,
                                    self.trigger_death_particles,
                                    self.add_xp,
                                )

    def damage_player(self, damage, attack_type):
        if self.player.can_be_hit:
            self.player.health -= damage
            self.player.can_be_hit = False
            self.animation_player.create_particles(
                attack_type, self.player.rect.center, [self.visible_sprites]
            )

    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(
                    attack_sprite, self.attackable_sprites, False
                )
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if (
                            isinstance(target_sprite, Tile)
                            and target_sprite.sprite_type == "grass"
                        ):
                            pos = (
                                target_sprite.rect.center
                                - pygame.math.Vector2(0, 40)
                            )
                            for _ in range(randint(5, 10)):
                                self.animation_player.create_grass_particles(
                                    pos, [self.visible_sprites]
                                )
                            target_sprite.kill()
                        else:
                            target_sprite.get_damage(
                                self.player, attack_sprite.sprite_type
                            )

    def trigger_death_particles(self, pos, particle_type):
        self.animation_player.create_particles(
            particle_type, pos, [self.visible_sprites]
        )

    def run(self):
        """Metoda pro načtení levelu"""
        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player)

        if self.game_paused:
            self.upgrade.display()
        else:
            self.visible_sprites.update()
            self.visible_sprites.enemy_update(self.player)
            self.player_attack_logic()

        # debug(self.player.weapon)


class YSortCameraGroup(
    pygame.sprite.Group
):  # overlap fix pro sprity na ose y, fake depth
    def __init__(self) -> None:
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.HALF_WIDTH = self.display_surface.get_width() // 2
        self.HALF_HEIGHT = self.display_surface.get_height() // 2
        self.offset = pygame.math.Vector2(0, 0)

        # obrázek na pozadí
        self.floor = pygame.image.load(
            "../graphics/tilemap/ground.png"
        ).convert()
        self.floor_rect = self.floor.get_rect(topleft=(0, 0))

    def enemy_update(self, player):
        enemies = [
            sprite for sprite in self.sprites() if isinstance(sprite, Enemy)
        ]
        for enemy in enemies:
            enemy.enemy_update(player)

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - self.HALF_WIDTH
        self.offset.y = (
            player.rect.centery - self.HALF_HEIGHT
        )  # hráč je tím pádem vždy uprostřed obrazovky, a zbytek se vykresluje dynamicky s offsetem

        self.display_surface.blit(
            self.floor, self.floor_rect.topleft - self.offset
        )

        for sprite in sorted(
            self.sprites(), key=lambda sprite: sprite.rect.centery
        ):  # seřadíme sprity podle jejich y pozice, pokud jdeš zdola tak máš větší y, pokud shora, tak obstacle má větší y
            offset_rect = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_rect)
