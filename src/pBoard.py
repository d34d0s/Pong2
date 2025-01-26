import random
import pygame as pg
from pygame.math import Vector2

import gfx
import pBar, pPuck

class PBoard:
    def __init__(self, windowSize:list[int]) -> None:
        pg.font.init()
        self.font: pg.Font = pg.Font("assets/fonts/megamax.ttf", 24)

        self.windowSize:list[int] = windowSize
        self.halfMark:pg.Surface = gfx.createSurface([2, windowSize[1]], [0, 0, 0])
        self.leftGoal:pg.Surface = gfx.createSurface([100, windowSize[1]], [0, 0, 0])
        self.rightGoal:pg.Surface = gfx.createSurface([100, windowSize[1]], [0, 0, 0])

        self.puckSize = Vector2(32, 32)
        self.puckSpawn = Vector2(
            self.windowSize[0] / 2 - (self.puckSize[0] / 2),
            self.windowSize[1] / 2 - self.puckSize[1] / 2
        )

        self.barSize = Vector2(32, self.windowSize[1] / 4)
        self.barSpawn1 = Vector2(
            self.windowSize[0] / 8,
            self.windowSize[1] / 2 - self.barSize[1] / 2
        )
        self.barSpawn2 = Vector2(
            self.windowSize[0] - self.barSpawn1[0] - self.barSize[0],
            self.barSpawn1[1]
        )

        self.puck:pPuck.PPuck = pPuck.PPuck(self.puckSize, self.puckSpawn.copy())
        self.player1: pBar.PBar = pBar.PBar(self.barSize, self.barSpawn1.copy(), color=[121, 240, 38], name="Player1")
        self.player2: pBar.PBar = pBar.PBar(self.barSize, self.barSpawn2.copy(), color=[63, 88, 240], name="Player2")

        self.winScore: int = 6
        self.players: dict[str, pBar.PBar] = {
            self.player1.name: {
                "score": 0,
                "bar": self.player1
            },
            self.player2.name: {
                "score": 0,
                "bar": self.player2
            },
        }

    def start(self) -> None:
        self.puck.location = self.puckSpawn.copy()
        self.puck.velocity[0] = random.choice([-self.puck.speed, self.puck.speed])
        self.puck.velocity[1] = random.choice([-self.puck.speed, self.puck.speed])
        
        self.player1.location = self.barSpawn1.copy()
        self.player2.location = self.barSpawn2.copy()

    def reset(self) -> None:
        self.puck.velocity = Vector2(0.0, 0.0)
        self.puck.location = self.puckSpawn.copy()
        
        self.player1.location = self.barSpawn1.copy()
        self.players[self.player1.name]["score"] = 0
        
        self.player2.location = self.barSpawn2.copy()
        self.players[self.player2.name]["score"] = 0

    def isGoal(self, puck: pPuck.PPuck) -> bool:
        result = False
        if (puck.location[0] + puck.size[0]) >= self.windowSize[0]:
            self.players[self.player1.name]["score"] += 1
            result = True
        elif puck.location[0] <= 0:
            self.players[self.player2.name]["score"] += 1
            result = True
        return result

    def handleScores(self, window: pg.Surface, deltaTime: float) -> None:
        score1 = self.players[self.player1.name]["score"]
        score1Text = f"{self.player1.name}: {score1}"
        score1Surface: pg.Surface = self.font.render(
            antialias=True, color=self.player1.color,
            text=score1Text
        )
        score1Location = [100, 0]

        score2 = self.players[self.player2.name]["score"]
        score2Text = f"{self.player2.name}: {score2}"
        score2Surface: pg.Surface = self.font.render(
            antialias=True, color=self.player2.color,
            text=score2Text
        )
        score2Location = [
            (self.windowSize[0] - self.rightGoal.get_size()[0]) - score2Surface.get_size()[0],
            0
        ]

        window.blit(score1Surface, score1Location)
        window.blit(score2Surface, score2Location)

    def render(self, window: pg.Surface, deltaTime: float) -> None:
        window.blit(self.leftGoal, [0, 0])
        window.blit(self.halfMark, [self.windowSize[0] / 2, 0])
        window.blit(self.rightGoal, [self.windowSize[0] - self.rightGoal.get_size()[0], 0])
        self.handleScores(window, deltaTime)

    def update(self, deltaTime:float) -> None:
        self.puck.update(deltaTime)
        self.isGoal(self.puck)

        # player halfMark bound
        if self.player1.location[0] + self.player1.size[0] > self.windowSize[0] / 2:
            self.player1.location[0] = self.windowSize[0] / 2 - self.player1.size[0]
        if self.player2.location[0] < self.windowSize[0] / 2 + self.halfMark.get_size()[0]:
            self.player2.location[0] = self.windowSize[0] / 2 + self.halfMark.get_size()[0]
        
        for player in self.players:
            playerBar = self.players[player]["bar"]
            playerBar.update(deltaTime)

            # player window bound x
            if playerBar.location[0] < 0:
                playerBar.location[0] = 0
            if playerBar.location[0] + playerBar.size[0] > self.windowSize[0]:
                playerBar.location[0] = self.windowSize[0] - playerBar.size[0]

            # player window bound y
            if playerBar.location[1] < 0:
                playerBar.location[1] = 0
            if playerBar.location[1] + playerBar.size[1] > self.windowSize[1]:
                playerBar.location[1] = self.windowSize[1] - playerBar.size[1]
