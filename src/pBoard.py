import random
import pygame as pg
from pygame.math import Vector2

import gfx, vfx, sfx
import pBar, pPuck

class PBoard:
    def __init__(
            self,
            windowSize:list[int],
            renderer: gfx.Renderer,
            assetManager: gfx.AssetManager,
            soundManager: sfx.SoundManager,
            particleSystem: gfx.ParticleSystem
        ) -> None:
        pg.font.init()
        self.font: pg.Font = pg.Font("assets/fonts/megamax.ttf", 24)

        self.windowSize:list[int] = windowSize
        self.renderer: gfx.Renderer = renderer
        self.assetManager: gfx.AssetManager = assetManager
        self.soundManager: sfx.SoundManager = soundManager
        self.particleSystem: gfx.ParticleSystem = particleSystem

        self.puckSize = [48, 48]
        self.puckSpawn = Vector2(
            self.windowSize[0] / 2 - (self.puckSize[0] / 2),
            self.windowSize[1] / 2 - self.puckSize[1] / 2
        )

        self.barSize = [32, self.windowSize[1] / 4]
        self.barSpawn1 = Vector2(
            self.windowSize[0] / 8,
            self.windowSize[1] / 2 - self.barSize[1] / 2
        )
        self.barSpawn2 = Vector2(
            self.windowSize[0] - self.barSpawn1[0] - self.barSize[0],
            self.barSpawn1[1]
        )

        self.matchInfo: dict = {
            "max": 3,
            "time": 0.0,
            "countdown": 0,
            "gameover": False,
            "mode": "classic",
            
            "boardInfo": {
                "puck": pPuck.PPuck(self.puckSize, self.puckSpawn),
                "halfMark": {
                    "size": [2, windowSize[1]],
                    "location": [self.windowSize[0] / 2, 0]
                },
                "leftGoal": {
                    "size": [16, windowSize[1]],
                    "location": [0, 0]
                },
                "rightGoal":{
                    "size": [16, windowSize[1]],
                    "location": [self.windowSize[0] - 16, 0]
                },
            },

            "playerInfo": {
                "player1": {
                    "score": 0,
                    "location": [0.0, 0.0],
                    "username": "Pong2Player1",
                    "bar": pBar.PBar(
                        facing=1,
                        size=self.barSize,
                        location=self.barSpawn1,
                        color=[255, 0, 17], name="Pong2Player1"
                    )
                },
                "player2": {
                    "score": 0,
                    "location": [0.0, 0.0],
                    "username": "Pong2_Player2",
                    "bar": pBar.PBar(
                        facing=-1,
                        size=self.barSize,
                        location=self.barSpawn2,
                        color=[0, 81, 255], name="Pong2_Player2"
                    )
                }
            }
        }

        self.puck: pPuck.PPuck = self.matchInfo["boardInfo"]["puck"]
        self.player1: pBar.PBar = self.matchInfo["playerInfo"]["player1"]["bar"]
        self.player2: pBar.PBar = self.matchInfo["playerInfo"]["player2"]["bar"]
        self.players: list[pBar.PBar] = [self.player1, self.player2]
 
        self.halfMark: gfx.Sprite = gfx.Sprite(
            self.matchInfo["boardInfo"]["halfMark"]["size"], 0.0,
            self.matchInfo["boardInfo"]["halfMark"]["location"],
            [10, 10, 10]
        )
        self.leftGoal: gfx.Sprite = gfx.Sprite(
            self.matchInfo["boardInfo"]["leftGoal"]["size"], 0.0,
            self.matchInfo["boardInfo"]["leftGoal"]["location"],
            [10, 10, 10]
        )
        self.rightGoal: gfx.Sprite = gfx.Sprite(
            self.matchInfo["boardInfo"]["rightGoal"]["size"], 0.0,
            self.matchInfo["boardInfo"]["rightGoal"]["location"],
            [10, 10, 10]
        )

        self.renderer.addSprite(self.leftGoal)
        self.renderer.addSprite(self.halfMark)
        self.renderer.addSprite(self.rightGoal)
               
        self.renderer.addSprite(self.puck)
        self.renderer.addSprite(self.player1)
        self.renderer.addSprite(self.player2)

    def getPlayerInfo(self, field: str) -> dict:
        try:
            return {
                "player1": self.matchInfo["playerInfo"]["player1"].copy().pop(field),
                "player2": self.matchInfo["playerInfo"]["player2"].copy().pop(field)
            }
        except KeyError as e:
            print(f"playerInfo key not found: {field} | {e}\n")
            return {}

    def start(self) -> None:
        self.puck.location = self.puckSpawn.copy()
        self.puck.velocity[0] = random.choice([-self.puck.speed, self.puck.speed])
        self.puck.velocity[1] = random.choice([-self.puck.speed, self.puck.speed])
        
    def midReset(self) -> None:
        self.matchInfo["countdown"] = 3
        self.puck.velocity = Vector2(0.0, 0.0)
        self.puck.location = self.puckSpawn.copy()
    
    def fullReset(self) -> None:
        self.matchInfo["time"] = 0.0
        self.matchInfo["countdown"] = 3
        self.matchInfo["gameover"] = False
        self.puck.velocity = Vector2(0.0, 0.0)
        self.puck.location = self.puckSpawn.copy()
        self.player1.location = self.barSpawn1.copy()
        self.player2.location = self.barSpawn2.copy()
        self.matchInfo["playerInfo"]["player1"]["score"] = 0
        self.matchInfo["playerInfo"]["player2"]["score"] = 0

    def isGoal(self, puck: pPuck.PPuck) -> int: # ret: 0 = No goal, 1 = goal, 2 = game over
        result = 0
        score1 = self.matchInfo["playerInfo"]["player1"]["score"]
        score2 = self.matchInfo["playerInfo"]["player2"]["score"]
        if score1 == self.matchInfo["max"]:
            vfx.PPuckWin(
                {"location": [self.rightGoal.location[0], self.puck.location[1] - self.rightGoal.location[1]], "player": self.player1},
                self.assetManager, self.particleSystem
            )
            print(f"Player 1 Wins!")
            return 2
        elif score2 == self.matchInfo["max"]:
            vfx.PPuckWin(
                {"location": [self.leftGoal.location[0], self.puck.location[1] - self.leftGoal.location[1]], "player": self.player2},
                self.assetManager, self.particleSystem
            )
            print(f"Player 2 Wins!")
            return 2

        if (puck.location[0] + puck.size[0]) >= self.windowSize[0]:
            vfx.PPuckGoal(
                {"location": [self.rightGoal.location[0], self.puck.location[1] - self.rightGoal.location[1]], "player": self.player1},
                self.assetManager, self.particleSystem
            )
            self.matchInfo["playerInfo"]["player1"]["score"] += 1
            result = 1
        elif puck.location[0] <= 0:
            vfx.PPuckGoal(
                {"location": [self.leftGoal.location[0], self.puck.location[1] - self.leftGoal.location[1]], "player": self.player2},
                self.assetManager, self.particleSystem
            )
            self.matchInfo["playerInfo"]["player2"]["score"] += 1
            result = 1
        return result

    def render(self, window: pg.Surface) -> None:
        score1 = self.matchInfo["playerInfo"]["player1"]["score"]
        score1Text = f"{self.player1.name}: {score1} {"".join(["|" for _ in range(score1)])}"
        score1Surface: pg.Surface = self.font.render(
            antialias=True, color=self.player1.color,
            text=score1Text
        )
        score1Location = [self.leftGoal.size[0], 0]

        score2 = self.matchInfo["playerInfo"]["player2"]["score"]
        score2Text = f"{"".join(["|" for _ in range(score2)])} {score2} :{self.player2.name}"
        score2Surface: pg.Surface = self.font.render(
            antialias=True, color=self.player2.color,
            text=score2Text
        )
        score2Location = [
            self.windowSize[0] - (self.rightGoal.size[0] + score2Surface.get_size()[0]),
            0
        ]

        window.blit(score1Surface, score1Location)
        window.blit(score2Surface, score2Location)

    def update(self, deltaTime:float) -> None:
        if not self.matchInfo["gameover"]:
            self.matchInfo["time"] += deltaTime
        
            if self.matchInfo["countdown"] > 0:
                self.matchInfo["countdown"] -= 1 * deltaTime
                if self.matchInfo["countdown"] <= 0:
                    self.matchInfo["countdown"] = 0
                    self.start()

            self.puck.update(deltaTime)
            goal = self.isGoal(self.puck)
            if goal == 1:   # goal
                self.midReset()
            elif goal == 2: # game ended
                self.matchInfo["gameover"] = True

        # player halfMark bound
        if self.player1.location[0] + self.player1.size[0] > self.windowSize[0] / 2:
            self.player1.location[0] = self.windowSize[0] / 2 - self.player1.size[0]
        if self.player2.location[0] < self.windowSize[0] / 2 + self.halfMark.size[0]:
            self.player2.location[0] = self.windowSize[0] / 2 + self.halfMark.size[0]
        
        for player in self.players:
            player.update(deltaTime)

            # player window bound x
            if player.location[0] < 0:
                player.location[0] = 0
            if player.location[0] + player.size[0] > self.windowSize[0]:
                player.location[0] = self.windowSize[0] - player.size[0]

            # player window bound y
            if player.location[1] < 0:
                player.location[1] = 0
            if player.location[1] + player.size[1] > self.windowSize[1]:
                player.location[1] = self.windowSize[1] - player.size[1]

