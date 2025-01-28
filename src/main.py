
import random
import pygame as pg
import gfx, sfx, vfx, events, inputs

import pBar, pPuck, physics, pBoard
from backend import  client

class Pong2:
    class state:
        running:bool = True
        deltaTime:float = 0.0
        clearColor:list[int] = [0, 0, 0]

    class settings:
        fps:float = 75.0
        sfxVolume: float = 15.5
        windowSize:list[int] = [1280, 720]

    def loadAssets(self) -> None:
        self.assets.loadImage("logo", "assets/logo.png")
        self.sounds.loadSound("puck", "assets/sfx/puck.mp3", self.settings.sfxVolume)
        self.sounds.loadSound("puck2", "assets/sfx/puck2.mp3", self.settings.sfxVolume)

    def __init__(self) -> None:
        self.clock = pg.time.Clock()
        
        self.window: gfx.Window = gfx.Window(*self.settings.windowSize, "Pong2")

        self.sounds = sfx.SoundManager()
        self.renderer = gfx.Renderer()
        self.events = events.EventHandler()
        self.particles = gfx.ParticleSystem(self.renderer, [0, 0], 10_000)
        
        self.assets = gfx.AssetManager()
        self.loadAssets()
        pg.display.set_icon(self.assets.getImage("logo"))
       
        self.board:pBoard.PBoard = pBoard.PBoard(
            self.settings.windowSize,
            self.renderer,
            self.assets,
            self.sounds,
            self.particles
        )
        self.physics = physics.PPhysics(self.board)

        self.devDisplay = gfx.DevDisplay([200, 200], [0, self.window.size[1] - 100], "assets/fonts/megamax.ttf")
        self.client = client.P2Client("D34D.DEV", [*self.board.player1.location])

    def update(self) -> None:
        self.devDisplay.setTextField("DT", f"{self.state.deltaTime}")
        self.devDisplay.setTextField("FPS", f"{self.clock.get_fps()}")

        if self.events.keyPressed(inputs.Keyboard.Escape): self.state.running = False
        
        if self.events.keyTriggered(inputs.Keyboard.F1): self.board.start()
        if self.events.keyTriggered(inputs.Keyboard.F2): self.board.fullReset()

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

    def postProcessing(self) -> None:
        # puck VFX
        # puck trail effect
        if self.board.puck.velocity[0] != 0 or self.board.puck.velocity[1] != 0:
            vfx.PPuckTrail({"puck": self.board.puck}, self.assets, self.particles)
        
        # puck on-hit effect
        if self.board.puck.hit:
            vfx.PPuckCollision({"puck": self.board.puck}, self.assets, self.particles)

        # player VFX
        for player in self.board.players:
            # bar flash effect
            if player.flashTime:
                vfx.PBarFlash({"player": player}, self.assets, self.particles)
            
            # bar trail effect
            if player.velocity[0] != 0 or player.velocity[1] != 0:
                vfx.PBarTrail({"player": player, "particleSize": [4, 4]}, self.assets, self.particles)
        self.particles.update(self.state.deltaTime)

    def render(self) -> None:
        self.window.fill(self.state.clearColor)
        self.board.render(self.window.display)
        self.renderer.render(self.window.display)
        self.postProcessing()
        self.devDisplay.render(self.window)
        self.window.render()
 
    def run(self) -> None:
        while self.state.running and self.events.update():
            self.update()
            self.render()
            self.state.deltaTime = self.clock.tick(self.settings.fps) / 1000.0 # ms -> sec

Pong2().run()
