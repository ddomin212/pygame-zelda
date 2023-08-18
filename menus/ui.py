import pygame

from helpers.settings import *


class UI:
    def __init__(self) -> None:
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        self.health_bar_rect = pygame.Rect(
            10, 10, HEALTH_BAR_WIDTH, BAR_HEIGHT
        )
        self.energy_bar_rect = pygame.Rect(
            10, 34, ENERGY_BAR_WIDTH, BAR_HEIGHT
        )

        self.weapon_graphics = [
            pygame.image.load(val["graphic"]).convert_alpha()
            for val in list(weapon_data.values())
        ]

        self.magic_graphics = [
            pygame.image.load(val["graphic"]).convert_alpha()
            for val in list(magic_data.values())
        ]

    def show_bar(self, current, max, bgrect, color):
        # draw bg
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bgrect)

        # converting health into pixels
        ratio = current / max
        current_width = bgrect.width * ratio
        new_rect = bgrect.copy()
        new_rect.width = current_width

        # drawing the bar
        pygame.draw.rect(self.display_surface, color, new_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bgrect, 3)

    def show_exp(self, exp):
        text_surface = self.font.render(str(int(exp)), False, TEXT_COLOR)
        x = self.display_surface.get_width() - 10
        y = self.display_surface.get_height() - 10
        text_rectangle = text_surface.get_rect(bottomright=(x, y))

        pygame.draw.rect(
            self.display_surface, UI_BG_COLOR, text_rectangle.inflate(10, 10)
        )

        self.display_surface.blit(text_surface, text_rectangle)

        pygame.draw.rect(
            self.display_surface,
            UI_BORDER_COLOR,
            text_rectangle.inflate(10, 10),
            3,
        )

    def selection_box(self, left, top, has_switched):
        bg_rect = pygame.Rect(left, top, ITEM_BOX_SIZE, ITEM_BOX_SIZE)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        if has_switched:
            pygame.draw.rect(
                self.display_surface, UI_BORDER_COLOR_ACTIVE, bg_rect, 3
            )
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        return bg_rect

    def weapon_overlay(self, weapon_index, has_switched):
        bg_rect = self.selection_box(10, 630, has_switched)
        weapon_surface = self.weapon_graphics[weapon_index]
        weapon_rect = weapon_surface.get_rect(center=bg_rect.center)

        self.display_surface.blit(weapon_surface, weapon_rect)

    def magic_overlay(self, magic_index, has_switched):
        bg_rect = self.selection_box(80, 635, has_switched)
        weapon_surface = self.magic_graphics[magic_index]
        weapon_rect = weapon_surface.get_rect(center=bg_rect.center)

        self.display_surface.blit(weapon_surface, weapon_rect)

    def display(self, player):
        self.show_bar(
            player.health,
            player.stats["health"],
            self.health_bar_rect,
            HEALTH_COLOR,
        )
        self.show_bar(
            player.energy,
            player.stats["energy"],
            self.energy_bar_rect,
            ENERGY_COLOR,
        )

        self.show_exp(player.exp)

        self.weapon_overlay(player.weapon_index, not player.can_weapon_switch)
        self.magic_overlay(player.magic_index, not player.can_magic_switch)
