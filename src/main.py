import random
from pygame.math import Vector2
import pygame as pg, d34dnet as dnet
import gfx, sfx, vfx, events, inputs

import pBar, pPuck, physics, pBoard

class Pong2(dnet.inet.BaseClient):
    class game_state:
        pong2id: str = None
        player_id: str = None
        opponent_id: str = None
        running: bool = True
        deltaTime: float = 0.0
        clearColor: list[int] = [0, 0, 0]


    class settings:
        fps:float = 75.0
        sfxVolume: float = 15.5
        windowSize: list[int] = [1280, 720]

    def loadAssets(self) -> None:
        self.assets.loadImage("logo", "assets/logo.png")
        self.sounds.loadSound("puck", "assets/sfx/puck.mp3", self.settings.sfxVolume)
        self.sounds.loadSound("puck2", "assets/sfx/puck2.mp3", self.settings.sfxVolume)

    def __init__(self) -> None:
        super().__init__()
        self.clock = pg.time.Clock()
        
        self.window: gfx.Window = gfx.Window(*self.settings.windowSize, "Pong2")

        self.sounds = sfx.SoundManager()
        self.renderer = gfx.Renderer()
        self.events = events.EventHandler()
        self.particles = gfx.ParticleSystem(self.renderer, [0, 0], 10_000)
        
        self.assets = gfx.AssetManager()
        self.loadAssets()
        pg.display.set_icon(self.assets.getImage("logo"))

        self.board: pBoard.PBoard = pBoard.PBoard(
            self.settings.windowSize,
            self.renderer,
            self.assets,
            self.sounds,
            self.particles
        )
        self.physics = physics.PPhysics(self.board)

        self.player = self.board.player1
        self.opponent = self.board.player2
        self.devDisplay = gfx.DevDisplay([200, 200], [0, self.window.size[1] - 100], "assets/fonts/megamax.ttf")

        # self.set_state("log-stdout", False)

    def on_connect(self):
        self.log_stdout(f"pong2 client connected to server: {self.address}")

    def on_disconnect(self):
        self.write(self.build_request("disconnect", {"pid": self.pid}))
 
    def on_write(self, request) -> None:
        self.log_stdout(f"request sent: {request}")

    def on_read(self, response: dict) -> None:
        method = response.get("method")
        params = response.get("params")
        match method.lower():
            case "join":
                self.game_state.pong2id = params.get("pong2id")
                if "1" in self.game_state.pong2id:
                    self.player = self.board.player1
                    self.opponent = self.board.player2
                    self.game_state.player_id = "player1"
                    self.game_state.opponent_id = "player2"
                else:
                    self.player = self.board.player2
                    self.opponent = self.board.player1
                    self.game_state.player_id = "player2"
                    self.game_state.opponent_id = "player1"
            case "update":
                player_info = params.pop(self.game_state.pong2id)
                self.player.location = Vector2(player_info["location"])
                self.player.velocity = Vector2(player_info["velocity"])
                try:
                    opponent_pong2id = self.game_state.opponent_id.replace("player", "p")
                    pucklocation = params.get("pucklocation")
                    puckvelocity = params.get("puckvelocity")
                    opponent_info = params.pop(opponent_pong2id)
                    self.opponent.location = Vector2(opponent_info["location"])
                    self.opponent.velocity = Vector2(opponent_info["velocity"])
                    if self.game_state.player_id == "player2":  # player2 board state based on host
                        self.board.puck.location = Vector2(pucklocation)
                        self.board.puck.velocity = Vector2(puckvelocity)
                except KeyError as e: pass # no other player connected!

    def update(self) -> None:
        self.devDisplay.setTextField("DT", f"{self.game_state.deltaTime}")
        self.devDisplay.setTextField("FPS", f"{self.clock.get_fps()}")

        if self.events.keyPressed(inputs.Keyboard.Escape): self.game_state.running = False
        
        if self.events.keyTriggered(inputs.Keyboard.F1): self.board.start()
        if self.events.keyTriggered(inputs.Keyboard.F2): self.board.fullReset()
        if self.events.keyTriggered(inputs.Keyboard.F3): self.connect()

        if self.events.keyPressed(inputs.Keyboard.A): self.player.moveLeft()
        if self.events.keyPressed(inputs.Keyboard.D): self.player.moveRight()
        if self.events.keyPressed(inputs.Keyboard.W): self.player.moveUp()
        if self.events.keyPressed(inputs.Keyboard.S): self.player.moveDown()
        
        self.physics.update(
            self.settings.windowSize,
            self.game_state.deltaTime,
            self.particles,
            self.sounds
        )
        self.board.update(self.game_state.deltaTime)

        self.write(self.build_request("update", {
            "velocity": [*self.player.velocity],
            "location": [*self.player.location],
            "puckvelocity": [*self.board.puck.velocity],
            "pucklocation": [*self.board.puck.location],
            "pong2id": self.game_state.pong2id
        }))
       
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
        self.particles.update(self.game_state.deltaTime)

    def render(self) -> None:
        self.window.fill(self.game_state.clearColor)
        self.board.render(self.window.display)
        self.renderer.render(self.window.display)
        self.postProcessing()
        self.devDisplay.render(self.window)
        self.window.render()
 
    def run(self) -> None:
        while self.game_state.running and self.events.update():
            self.update()
            self.render()
            self.game_state.deltaTime = self.clock.tick(self.settings.fps) / 1000.0 # ms -> sec
        self.disconnect()

Pong2().run()
