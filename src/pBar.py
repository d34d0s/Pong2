import gfx
from pygame.math import Vector2

class PBar(gfx.Sprite):
    def __init__(self, size, location, color = [255, 255, 255], name:str = "Pong2.Player"):
        super().__init__(size, location, color)
        self.rotation = 0.0
        self.speed = 500.0 # px/sec
        self.name: str = name

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
