import random
import pygame as pg
from pygame.math import Vector2

import gfx
import pBar, pPuck

class PBoard:
    def __init__(self, windowSize:list[int]) -> None:
        pg.font.init()
        self.font: pg.Font = pg.Font("assets/fonts/megamax.ttf", 18)

        self.windowSize:list[int] = windowSize

        self.winScore: int = 6
        self.scores: list[int] = [0, 0]

        self.halfMark:pg.Surface = gfx.createSurface([2, windowSize[1]], [0, 0, 0])
        self.leftGoal:pg.Surface = gfx.createSurface([100, windowSize[1]], [0, 0, 0])
        self.rightGoal:pg.Surface = gfx.createSurface([100, windowSize[1]], [0, 0, 0])

        self.puckSize = [16, 16]
        self.puckSpawn = [
            self.windowSize[0] / 2 - (self.puckSize[0] / 2),
            self.windowSize[1] / 2 - self.puckSize[1] / 2
        ]

        self.barSize = [16, self.windowSize[1] / 4]
        self.barSpawn1 = [
            self.windowSize[0] / 8,
            self.windowSize[1] / 2 - self.barSize[1] / 2
        ] 
        self.barSpawn2 = [
            self.windowSize[0] - self.barSpawn1[0] - self.barSize[0],
            self.barSpawn1[1]
        ]

        self.puck:pPuck.PPuck = None
        self.player1: pBar.PBar = pBar.PBar(self.barSize, self.barSpawn1, [255, 255, 255])
        self.player2: pBar.PBar = pBar.PBar(self.barSize, self.barSpawn2, [255, 255, 255])
        self.pucks:list[pPuck.PPuck] = [pPuck.PPuck([16, 16], self.puckSpawn.copy())]
        self.puck = self.pucks[len(self.pucks) - 1]
        self.players:list[pBar.PBar] = [self.player1, self.player2]

    def start(self) -> None:
        self.puck.velocity[0] = random.choice([-self.puck.speed, self.puck.speed])

    def reset(self) -> None:
        self.puck.velocity = Vector2(0.0, 0.0)
        self.puck.location = self.puckSpawn.copy()

    def isGoal(self, puck: pPuck.PPuck) -> bool:
        result = False
        if puck.velocity[0] < 0:
            if puck.location[0] + puck.size[0] <= -puck.size[0]:
                if self.scores[0] - 1 >= 0: self.scores[0] -= 1
                self.scores[1] += 1
                result = True

        if puck.velocity[0] > 0:
            if puck.location[0] >= self.windowSize[0] + puck.size[0]:
                self.scores[0] += 1
                if self.scores[1] - 1 >= 0: self.scores[1] -= 1
                result = True
        return result

    def renderScores(self, target: pg.Surface) -> None:
        score1: pg.Surface = self.font.render(f"{self.player1.name}: {self.scores[0]}", antialias=True, color=[255, 255, 255])
        scorePos1 = [100, 0]

        score2: pg.Surface = self.font.render(f"{self.player2.name}: {self.scores[1]}", antialias=True, color=[255, 255, 255])
        scorePos2 = [
            self.windowSize[0] - self.rightGoal.get_size()[0] - score2.get_size()[0],
            0
        ]
        
        target.blit(score1, scorePos1)
        target.blit(score2, scorePos2)

    def render(self, target: pg.Surface) -> None:
        target.blit(self.leftGoal, [0, 0])
        target.blit(self.halfMark, [self.windowSize[0] / 2, 0])
        target.blit(self.rightGoal, [self.windowSize[0] - self.rightGoal.get_size()[0], 0])
        self.renderScores(target)

    def update(self, deltaTime:float) -> None:
        for puck in self.pucks:
            puck.update(deltaTime)
            
            if self.isGoal(puck):
                self.reset()

        # player halfMark bound
        if self.player1.location[0] + self.player1.size[0] > self.windowSize[0] / 2:
            self.player1.location[0] = self.windowSize[0] / 2 - self.player1.size[0]
        if self.player2.location[0] < self.windowSize[0] / 2 + self.halfMark.get_size()[0]:
            self.player2.location[0] = self.windowSize[0] / 2 + self.halfMark.get_size()[0]
        
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
