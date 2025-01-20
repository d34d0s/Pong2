
import random
import pygame as pg
import gfx, sfx, events, inputs

import pBar, pPuck, physics, pBoard

class Pong2:
    class state:
        running:bool = True
        deltaTime:float = 0.0
        clearColor:list[int] = [10, 10, 10]

    class settings:
        fps:float = 60.0
        # windowSize:list[int] = [400, 300]
        # windowSize:list[int] = [800, 600]
        windowSize:list[int] = [1280, 720]

        barSpeed:float = 500.0

    def loadAssets(self) -> None:
        self.assets.loadImage("logo", "assets/logo.png")
        self.sounds.loadSound("puck", "assets/sfx/puck.mp3", 20)
        self.sounds.loadSound("puck2", "assets/sfx/puck2.mp3", 20)

    def __init__(self) -> None:
        self.clock = pg.time.Clock()
        
        self.window = pg.display.set_mode(self.settings.windowSize, pg.WINDOWPOS_CENTERED)
        pg.display.set_caption("Pong2")

        self.sounds = sfx.SoundHandler()
        self.renderer = gfx.Renderer()
        self.events = events.EventHandler()
        self.particles = gfx.ParticleSystem(self.renderer, [0, 0], 100)
        
        self.assets = gfx.AssetManager()
        self.loadAssets()
        pg.display.set_icon(self.assets.getImage("logo"))
       
        self.board:pBoard.PBoard = pBoard.PBoard(self.settings.windowSize)
        [self.renderer.addSprite(puck) for puck in self.board.pucks]
        [self.renderer.addSprite(player) for player in self.board.players]
        self.physics = physics.PPhysics(self.board)
    
    def update(self) -> None:
        if self.events.keyPressed(inputs.Keyboard.Escape): self.state.running = False
        
        if self.events.keyPressed(inputs.Keyboard.F1): self.board.start()
        if self.events.keyPressed(inputs.Keyboard.F2): self.board.reset()

        if self.events.keyPressed(inputs.Keyboard.A):self.board.player1.moveLeft()
        if self.events.keyPressed(inputs.Keyboard.D):self.board.player1.moveRight()
        if self.events.keyPressed(inputs.Keyboard.W): self.board.player1.moveUp()
        if self.events.keyPressed(inputs.Keyboard.S): self.board.player1.moveDown()
        
        if self.events.keyPressed(inputs.Keyboard.Left):self.board.player2.moveLeft()
        if self.events.keyPressed(inputs.Keyboard.Right):self.board.player2.moveRight()
        if self.events.keyPressed(inputs.Keyboard.Up): self.board.player2.moveUp()
        if self.events.keyPressed(inputs.Keyboard.Down): self.board.player2.moveDown()

        self.particles.update(self.state.deltaTime)
        self.physics.update(
            self.settings.windowSize,
            self.state.deltaTime,
            self.sounds
        )
        self.board.update(self.state.deltaTime)

    def render(self) -> None:
        self.window.fill(self.state.clearColor)

        self.board.render(self.window)
        self.renderer.render(self.window)

        # post processing vfx
        [self.particles.addParticle(0.1, [4, 4], [player.location[0] + (player.size[0] / 2), player.location[1]], [0, -120]) for player in self.board.players if player.velocity[0] != 0 or player.velocity[1] != 0]
        [self.particles.addParticle(0.1, [4, 4], [player.location[0] + (player.size[0] / 2), player.location[1] + player.size[1]], [0, -120]) for player in self.board.players if player.velocity[0] != 0 or player.velocity[1] != 0]
        [self.particles.addParticle(0.1, [4, 4], [player.location[0] + (player.size[0] / 2), player.location[1] + (player.size[1] / 2)], [0, -120]) for player in self.board.players if player.velocity[0] != 0 or player.velocity[1] != 0]
        
        [self.particles.addParticle(0.1, [4, 4], [puck.location[0] + (puck.size[0] / 2), puck.location[1] + (puck.size[1] / 2)], [0, -120]) for puck in self.board.pucks if puck.velocity[0] != 0 or puck.velocity[1] != 0]
        
    def run(self) -> None:
        while self.state.running and self.events.update():
            self.state.deltaTime = self.clock.tick(self.settings.fps) / 1000.0 # ms -> sec
            self.update()
            self.render()
            pg.display.flip()    

Pong2().run()