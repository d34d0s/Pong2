import gfx
from pygame.math import Vector2

class PBar(gfx.Sprite):
    def __init__(self, facing: int, size, location, color=[255, 255, 255], name="Pong2.Player"):
        super().__init__(size, 550.0, location, color, rotate=True)
        self.name: str = name
        self.hit: bool = False
        self.flashTime: float = 0.0
        self.facing: int = facing # (specify which half of the court the pBar faces) -1 left | 1 right
        self.setImage(gfx.createSurfaceFADE(self.size, self.color, self.facing, 0))

        # player cosmetics (asset strs)
        self.barSkin: str = "default"
        self.winParticle: str = "how"
        self.goalParticle: str = "how"

    def onHit(self, rotSpeed: float) -> None:
        self.rotSpeed = rotSpeed
        self.flashTime = 0.2
        self.hit = True

    def update(self, deltaTime: float) -> None:
        super().update(deltaTime)
        if self.hit:
            self.rotation *= (60/100)
            if abs(self.rotation) < 0.1:
                self.rotSpeed = 0.0
                self.rotation = 0.0
                self.hit = False
        
        if self.flashTime > 0:
            self.flashTime -= 1 * deltaTime
            self.fillImage([255, 255, 255])
            if self.flashTime <= 0.0:
                self.flashTime = 0.0
                self.setImage(gfx.createSurfaceFADE(self.size, self.color, self.facing, 0))
