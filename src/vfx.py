import gfx
import random
import pygame as pg

class VFX:
    assetManager: gfx.AssetManager = None
    particleSystem: gfx.ParticleSystem = None
    
    def __init__(self, data: dict, assetManager: gfx.AssetManager, particleSystem: gfx.ParticleSystem) -> None:
        self.assetManager: gfx.AssetManager = assetManager
        self.particleSystem: gfx.ParticleSystem = particleSystem

""" PPuck VFX """
class PPuckTrail(VFX):
    def __init__(self, data: dict, assetManager: gfx.AssetManager, particleSystem: gfx.ParticleSystem) -> None:
        super().__init__(data, assetManager, particleSystem)
        puck = data["puck"]
        self.particleSystem.addParticle(
            0.1, random.choice([[pow(2, i+1), pow(2, i+1)] for i in range(4)]),
            [puck.location[0] + (puck.size[0] / 2), puck.location[1] + (puck.size[1] / 2)],
            velocity=[0, -120], color=puck.color, wireSize=2
        )

class PPuckCollision(VFX):
    def __init__(self, data: dict, assetManager: gfx.AssetManager, particleSystem: gfx.ParticleSystem) -> None:
        super().__init__(data, assetManager, particleSystem)
        puck = data["puck"]
        for i in range(random.randrange(25, 50)):
            self.particleSystem.addParticle(
                0.2, random.choice([[pow(2, i+1), pow(2, i+1)] for i in range(2)]),
                puck.location, [random.randrange(-80, 200), random.randrange(-80, 200)],
                wireSize=random.randint(1, 4)
            )
        puck.hit = False

class PPuckGoal(VFX):
    def __init__(self, data: dict, assetManager: gfx.AssetManager, particleSystem: gfx.ParticleSystem) -> None:
        super().__init__(data, assetManager, particleSystem)
        player = data["player"]
        for i in range(random.randrange(100, 400)):
            self.particleSystem.addParticle(
                3.5, random.choice([[pow(2, i+1), pow(2, i+1)] for i in range(4)]),
                data["location"], [random.randrange(-200, 400) * player.facing, random.randrange(-200, 400)],
                wireSize=random.randint(1, 4), color=player.color, asset=player.goalParticle
            )

class PPuckWin(VFX):
    def __init__(self, data: dict, assetManager: gfx.AssetManager, particleSystem: gfx.ParticleSystem) -> None:
        super().__init__(data, assetManager, particleSystem)
        player = data["player"]
        for i in range(random.randrange(500, 1500)):
            self.particleSystem.addParticle(
                3.4, random.choice([[pow(2, i+1), pow(2, i+1)] for i in range(4)]),
                data["location"], [random.randrange(-1200, 1200) * player.facing, random.randrange(-1200, 1200)],
                wireSize=1, color=player.color, asset=player.winParticle
            )

""" PBar VFX """
class PBarFlash(VFX):
    def __init__(self, data: dict, assetManager: gfx.AssetManager, particleSystem: gfx.ParticleSystem) -> None:
        super().__init__(data, assetManager, particleSystem)
        player = data["player"]
        self.particleSystem.addParticle(
            lifeSpan=0.1,
            size=player.size,
            location=player.location,
            velocity=[
                -(player.velocity[0] / abs(player.velocity[0] + 1)),
                -(player.velocity[1] / abs(player.velocity[1] + 1))
            ], color=player.color, wireSize=1
        )

class PBarTrail(VFX):
    def __init__(self, data: dict, assetManager: gfx.AssetManager, particleSystem: gfx.ParticleSystem) -> None:
        super().__init__(data, assetManager, particleSystem)
        player = data["player"]
        particleSize = data["particleSize"]

        # top bar trail
        self.particleSystem.addParticle(
            lifeSpan=0.1,
            size=particleSize,
            location=[player.location[0] + (player.size[0] / 2), player.location[1]],
            velocity=[0, -120], color=player.color, wireSize=1
        )
        # middle bar trail
        self.particleSystem.addParticle(
            lifeSpan=0.1,
            size=particleSize,
            location=[player.location[0] + (player.size[0] / 2), player.location[1] + (player.size[1] / 2)],
            velocity=[0, -120], color=player.color, wireSize=1
        )
        # bottom bar trail
        self.particleSystem.addParticle(
            lifeSpan=0.1,
            size=particleSize,
            location=[player.location[0] + (player.size[0] / 2), player.location[1] + player.size[1]],
            velocity=[0, -120], color=player.color, wireSize=1
        )

