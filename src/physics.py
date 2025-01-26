import sfx
import pBar, pPuck, pBoard

class PPhysics:
    def __init__(self, board: pBoard.PBoard) -> None:
        self.board: pBoard.PBoard = board

    def friction(self, player: pBar.PBar, deltaTime: float) -> None:
        if player.velocity[0] > 0:
            player.velocity[0] -= (player.speed * 4) * deltaTime
            if player.velocity[0] <= 0:
                player.velocity[0] = 0

        if player.velocity[0] < 0:
            player.velocity[0] += (player.speed * 4) * deltaTime
            if player.velocity[0] >= 0:
                player.velocity[0] = 0
        
        if player.velocity[1] > 0:
            player.velocity[1] -= (player.speed * 4) * deltaTime
            if player.velocity[1] <= 0:
                player.velocity[1] = 0

        if player.velocity[1] < 0:
            player.velocity[1] += (player.speed * 4) * deltaTime
            if player.velocity[1] >= 0:
                player.velocity[1] = 0
        
    def aabb(self, player: pBar.PBar, puck: pPuck.PPuck) -> bool:
        if (not(
            (puck.location[1] + puck.size[1]) < player.location[1] or
            puck.location[0] > (player.location[0] + player.size[0]) or
            puck.location[1] > (player.location[1] + player.size[1]) or
            (puck.location[0] + puck.size[0]) < player.location[0]
        )): return True
        else: return False

    def checkCollisions(self, soundHandler: sfx.SoundHandler) -> None:
        rot_speed = 200 * (-1 if self.board.puck.velocity[1] < 0 else 1)
        if self.aabb(self.board.player1, self.board.puck):
            soundHandler.playSound("puck")
            self.board.puck.location[0] = (self.board.player1.location[0] + self.board.player1.size[0]) + 1
            self.board.puck.velocity[0] = -self.board.puck.velocity[0]
            self.board.player1.onHit(rot_speed)

        if self.aabb(self.board.player2, self.board.puck):
            soundHandler.playSound("puck")
            self.board.puck.location[0] = (self.board.player2.location[0] - self.board.puck.size[0]) - 1
            self.board.puck.velocity[0] = -self.board.puck.velocity[0]
            self.board.player2.onHit(-rot_speed)

    def checkBounds(self, windowSize: list[int], soundHandler: sfx.SoundHandler) -> None:
        # puck vertical bounce
        if self.board.puck.location[1] <= 0:
            soundHandler.playSound("puck2")
            self.board.puck.location[1] = 1
            self.board.puck.velocity[1] = -self.board.puck.velocity[1]
        elif (self.board.puck.location[1] + self.board.puck.size[1]) >= windowSize[1]:
            soundHandler.playSound("puck2")
            self.board.puck.location[1] = (windowSize[1] - self.board.puck.size[1]) - 1
            self.board.puck.velocity[1] = -self.board.puck.velocity[1]

        # puck horizontal bounce
        if self.board.puck.location[0] <= 0:
            soundHandler.playSound("puck2")
            self.board.puck.location[0] = 1
            self.board.puck.velocity[0] = -self.board.puck.velocity[0]
        elif (self.board.puck.location[0] + self.board.puck.size[0]) >= windowSize[0]:
            soundHandler.playSound("puck2")
            self.board.puck.location[0] = (windowSize[0] - self.board.puck.size[0]) - 1
            self.board.puck.velocity[0] = -self.board.puck.velocity[0]

    def update(self, windowSize: list[int], deltaTime: float, soundHandler: sfx.SoundHandler) -> None:
        self.checkBounds(windowSize, soundHandler)
        self.checkCollisions(soundHandler)
        for player in self.board.players:
            self.friction(player, deltaTime)
