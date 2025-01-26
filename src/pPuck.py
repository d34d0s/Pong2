import gfx
import pBar

import pygame as pg

class PPuck(gfx.Sprite):
    def __init__(self, size, location, color = [255, 255, 255]):
        super().__init__(size, 500.0, location, color, rotate=True)

    def moveRight(self) -> None:
        self.velocity[0] = self.speed
    
    def moveLeft(self) -> None:
        self.velocity[0] = -self.speed
    
    def moveUp(self) -> None:
        self.velocity[1] = -self.speed
    
    def moveDown(self) -> None:
        self.velocity[1] = self.speed

    def update(self, deltaTime:float) -> None:
        super().update(deltaTime)
        self.rot_speed = (self.velocity[0] * 2)
