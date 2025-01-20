import gfx
import pBar

class PPuck(gfx.Sprite):
    def __init__(self, size, location, color = [255, 255, 255]):
        super().__init__(size, location, color)
        self.weight = 5.0
        self.speed = 500.0
        self.rotation = 0.0

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

