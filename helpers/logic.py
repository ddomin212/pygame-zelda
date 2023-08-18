import pygame


class Cooldown:
    def __init__(self, can, time, cooldown, call_fn=None):
        self.can = can
        self.time = time
        self.cooldown = cooldown
        self.call_fn = call_fn

    def cooldown_fn(self):
        if self.can is False:
            if self.time is None:
                self.time = pygame.time.get_ticks()
            if pygame.time.get_ticks() - self.time > self.cooldown:
                self.can = True
                self.time = None
                if self.call_fn is not None:
                    self.call_fn()
        return self.can, self.time, self.cooldown
