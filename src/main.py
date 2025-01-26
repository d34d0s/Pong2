
import random
import pygame as pg
import gfx, sfx, events, inputs

import pBar, pPuck, physics, pBoard
from backend import  client

class Pong2:
    class state:
        running:bool = True
        deltaTime:float = 0.0
        clearColor:list[int] = [10, 10, 10]

    class settings:
        fps:float = 75.0
        # windowSize:list[int] = [400, 300]
        # windowSize:list[int] = [800, 600]
        windowSize:list[int] = [1280, 720]

    def loadAssets(self) -> None:
        self.assets.loadImage("logo", "assets/logo.png")
        self.sounds.loadSound("puck", "assets/sfx/puck.mp3", 100)
        self.sounds.loadSound("puck2", "assets/sfx/puck2.mp3", 100)

    def __init__(self) -> None:
        self.clock = pg.time.Clock()
        
        self.window = pg.display.set_mode(self.settings.windowSize, pg.WINDOWPOS_CENTERED)
        pg.display.set_caption("Pong2")

        self.sounds = sfx.SoundHandler()
        self.renderer = gfx.Renderer()
        self.events = events.EventHandler()
        self.particles = gfx.ParticleSystem(self.renderer, [0, 0], 10_000)
        
        self.assets = gfx.AssetManager()
        self.loadAssets()
        pg.display.set_icon(self.assets.getImage("logo"))
       
        self.board:pBoard.PBoard = pBoard.PBoard(self.settings.windowSize)
        self.renderer.addSprite(self.board.puck)
        self.renderer.addSprite(self.board.player1)
        self.renderer.addSprite(self.board.player2)
        self.physics = physics.PPhysics(self.board)

        self.devDisplay = gfx.DevDisplay([200, 200], [0, self.window.get_size()[1] - 100], "assets/fonts/megamax.ttf")
        self.client = client.P2Client("D34D.DEV", [*self.board.player1.location])

    def update(self) -> None:
        self.devDisplay.setTextField("DT", f"{self.state.deltaTime}")
        self.devDisplay.setTextField("FPS", f"{self.clock.get_fps()}")

        if self.events.keyPressed(inputs.Keyboard.Escape): self.state.running = False
        
        if self.events.keyTriggered(inputs.Keyboard.F1): self.board.start()
        if self.events.keyTriggered(inputs.Keyboard.F2): self.board.reset()

        if self.events.keyPressed(inputs.Keyboard.A): self.board.player1.moveLeft()
        if self.events.keyPressed(inputs.Keyboard.D): self.board.player1.moveRight()
        if self.events.keyPressed(inputs.Keyboard.W): self.board.player1.moveUp()
        if self.events.keyPressed(inputs.Keyboard.S): self.board.player1.moveDown()
        
        if self.events.keyPressed(inputs.Keyboard.Left):self.board.player2.moveLeft()
        if self.events.keyPressed(inputs.Keyboard.Right):self.board.player2.moveRight()
        if self.events.keyPressed(inputs.Keyboard.Up): self.board.player2.moveUp()
        if self.events.keyPressed(inputs.Keyboard.Down): self.board.player2.moveDown()

        self.physics.update(
            self.settings.windowSize,
            self.state.deltaTime,
            self.particles,
            self.sounds
        )
        self.board.update(self.state.deltaTime)
        self.particles.update(self.state.deltaTime)

    def postProcessing(self) -> None:
        # bar particles
        barParticleSize = [4, 4]
        for player in self.board.players:
            playerBar = self.board.players[player]["bar"]
            if playerBar.velocity[0] != 0 or playerBar.velocity[1] != 0:
                # full bar trail
                if playerBar.flashTime:
                    self.particles.addParticle(
                        lifeSpan=0.1,
                        size=playerBar.size,
                        location=playerBar.location,
                        velocity=[
                            -(playerBar.velocity[0] / abs(playerBar.velocity[0] + 1)),
                            -(playerBar.velocity[1] / abs(playerBar.velocity[1] + 1))
                        ], color=playerBar.color, wireSize=1
                    )
                # top bar trail
                self.particles.addParticle(
                    lifeSpan=0.1,
                    size=barParticleSize,
                    location=[playerBar.location[0] + (playerBar.size[0] / 2), playerBar.location[1]],
                    velocity=[0, -120], color=playerBar.color, wireSize=1
                )
                # middle bar trail
                self.particles.addParticle(
                    lifeSpan=0.1,
                    size=barParticleSize,
                    location=[playerBar.location[0] + (playerBar.size[0] / 2), playerBar.location[1] + (playerBar.size[1] / 2)],
                    velocity=[0, -120], color=playerBar.color, wireSize=1
                )
                # bottom bar trail
                self.particles.addParticle(
                    lifeSpan=0.1,
                    size=barParticleSize,
                    location=[playerBar.location[0] + (playerBar.size[0] / 2), playerBar.location[1] + playerBar.size[1]],
                    velocity=[0, -120], color=playerBar.color, wireSize=1
                )
        
        # puck particles
        if self.board.puck.velocity[0] != 0 or self.board.puck.velocity[1] != 0:
            sizes = lambda x: [[pow(2, i+1), pow(2, i+1)] for i in range(x)]
            self.particles.addParticle(
                0.1, random.choice(sizes(4)),
                [self.board.puck.location[0] + (self.board.puck.size[0] / 2), self.board.puck.location[1] + (self.board.puck.size[1] / 2)],
                velocity=[0, -120], color=self.board.puck.color, wireSize=2
            )

    def render(self) -> None:
        self.window.fill(self.state.clearColor)
        self.board.render(self.window, self.state.deltaTime)
        self.renderer.render(self.window)
        self.postProcessing()
        self.devDisplay.render(self.window)
 
    def run(self) -> None:
        while self.state.running and self.events.update():
            self.update()
            self.render()
            pg.display.flip()
            self.state.deltaTime = self.clock.tick(self.settings.fps) / 1000.0 # ms -> sec

Pong2().run()
