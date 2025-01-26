import gfx
from pygame.math import Vector2

class PBar(gfx.Sprite):
    def __init__(self, size, location, color=[255, 255, 255], name="Pong2.Player"):
        super().__init__(size, 500.0, location, color, rotate=True)
        self.name: str = name
        self.hit: bool = False

    def moveRight(self) -> None:
        self.velocity[0] = self.speed
    
    def moveLeft(self) -> None:
        self.velocity[0] = -self.speed
    
    def moveUp(self) -> None:
        self.velocity[1] = -self.speed
    
    def moveDown(self) -> None:
        self.velocity[1] = self.speed

    def onHit(self, rot_speed: float) -> None:
        self.rot_speed = rot_speed
        self.hit = True

    def update(self, deltaTime: float) -> None:
        super().update(deltaTime)
        if self.hit: self.rotation *= 0.9

