import gfx
from pygame.math import Vector2

class PBar(gfx.Sprite):
    def __init__(self, size, location, color=[255, 255, 255], name="Pong2.Player"):
        super().__init__(size, 500.0, location, color, rotate=True)
        self.name: str = name
        self.hit: bool = False
        self.flashTime: float = 0.0

    def onHit(self, rotSpeed: float) -> None:
        self.rotSpeed = rotSpeed
        self.flashTime = 0.2
        self.hit = True

    def update(self, deltaTime: float) -> None:
        super().update(deltaTime)
        if self.hit:
            self.rotation *= (40/100)
            if abs(self.rotation) < 0.1:
                self.rotSpeed = 0.0
                self.rotation = 0.0
                self.hit = False
        
        if self.flashTime > 0:
            self.flashTime -= 1 * deltaTime
            self.fillImage([255, 255, 255])
            if self.flashTime <= 0.0:
                self.flashTime = 0.0
                self.fillImage(self.color)
