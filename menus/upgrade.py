import pygame

from helpers.settings import *


class Upgrade:
    def __init__(self, player):
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.attribute_number = len(player.stats)
        self.attribute_names = list(player.stats.keys())
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        self.height = self.display_surface.get_height() * 0.8
        self.width = self.display_surface.get_width() // 6
        self.create_items()

        self.max_stats = list(player.max_stats.values())

        self.selection_idx = 0
        self.selection_time = None
        self.can_select = True

    def input(self):
        keys = pygame.key.get_pressed()
        if self.can_select is True:
            if (
                keys[pygame.K_RIGHT]
                and self.selection_idx < self.attribute_number - 1
            ):
                self.selection_idx = self.selection_idx + 1
                self.can_select = False
                self.selection_time = pygame.time.get_ticks()
            elif keys[pygame.K_LEFT] and self.selection_idx > 0:
                self.selection_idx = self.selection_idx - 1
                self.can_select = False
            if keys[pygame.K_SPACE]:
                self.can_select = False
                self.item_list[self.selection_idx].trigger(
                    self.player, self.attribute_names
                )

    def cooldown(self):
        if self.can_select is False:
            if self.selection_time is None:
                self.selection_time = pygame.time.get_ticks()
            if pygame.time.get_ticks() - self.selection_time > 500:
                self.can_select = True
                self.selection_time = None

    def create_items(self):
        self.item_list = []
        for i in range(self.attribute_number):
            increment = (
                self.display_surface.get_width() // self.attribute_number
            )
            left = (increment * i) + (increment - self.width) // 2
            top = self.display_surface.get_height() * 0.1
            item = Item(left, top, self.width, self.height, i, self.font)
            self.item_list.append(item)

    def display(self):
        self.input()
        self.cooldown()
        for idx, item in enumerate(self.item_list):
            item.display(
                self.display_surface,
                self.selection_idx,
                self.attribute_names[idx],
                self.player.get_value_by_index(idx),
                self.max_stats[idx],
                self.player.get_cost_by_index(idx),
            )


class Item:
    def __init__(self, l, t, w, h, index, font):
        self.rect = pygame.Rect(l, t, w, h)
        self.index = index
        self.font = font

    def display_names(self, surface, name, cost, selected):
        color = TEXT_COLOR_SELECTED if selected else TEXT_COLOR
        text_surface = self.font.render(name, False, color)
        text_rect = text_surface.get_rect(
            center=(self.rect.centerx, self.rect.top + 20)
        )
        surface.blit(text_surface, text_rect)

        text_surface = self.font.render(str(int(cost)), False, color)
        text_rect = text_surface.get_rect(
            center=(self.rect.centerx, self.rect.bottom - 20)
        )
        surface.blit(text_surface, text_rect)

    def display_bar(self, surface, current, max, selected):
        top = self.rect.midtop + pygame.math.Vector2(0, 60)
        bottom = self.rect.midbottom - pygame.math.Vector2(0, 60)
        ratio = (current / max) * (bottom.y - top.y)
        color = BAR_COLOR_SELECTED if selected else BAR_COLOR
        value_rect = pygame.Rect(top.x - 15, bottom.y - ratio, 30, 10)
        pygame.draw.line(surface, color, top, bottom, 5)
        pygame.draw.rect(surface, color, value_rect)

    def trigger(self, player, attribute_names):
        cost = player.get_cost_by_index(self.index)
        attr = attribute_names[self.index]
        if player.exp >= cost and player.stats[attr] < player.max_stats[attr]:
            player.exp -= cost
            player.stats[attr] *= 1.2
            player.upgrade_cost[attr] *= 1.4
        if player.stats[attr] >= player.max_stats[attr]:
            player.stats[attr] = player.max_stats[attr]

    def display(self, surface, selection_num, name, val, max, cost):
        selected = selection_num == self.index
        if selected:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR_ACTIVE, self.rect, 4)
        else:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)
        self.display_names(surface, name, cost, selected)
        self.display_bar(surface, val, max, selected)
