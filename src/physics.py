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
        
    def aabb(self, player: pBar.PBar, puck, soundHandler: sfx.SoundHandler) -> None:
        if puck.velocity[0] > 0:
            if puck.rect.colliderect(player.rect):
                soundHandler.playSound("puck")
                overlap = player.rect.left - puck.rect.right
                puck.location[0] += overlap
                puck.velocity[0] = -puck.speed
                puck.velocity[1] += (player.velocity[1] / 4)
                
                player.location[0] -= overlap
                
        elif puck.velocity[0] < 0:
            if puck.rect.colliderect(player.rect):
                soundHandler.playSound("puck")
                overlap = player.rect.right - puck.rect.left
                puck.location[0] += overlap
                puck.velocity[0] = puck.speed
                puck.velocity[1] += (player.velocity[1] / 4)
                
                player.location[0] -= overlap

    def checkBounds(self, windowSize: list[int], puck: pPuck.PPuck, soundHandler: sfx.SoundHandler) -> None:
        # puck vertical bounce
        if puck.velocity[1] < 0 and (puck.location[1] + 1) < 0:
            puck.velocity[1] = puck.speed
            puck.location[1] = 0
            soundHandler.playSound("puck2")
        if puck.velocity[1] > 0 and ((puck.location[1] + puck.size[1]) + 1) > windowSize[1] - puck.size[1]:
            puck.velocity[1] = -puck.speed
            puck.location[1] = windowSize[1] - puck.size[1]
            soundHandler.playSound("puck2")  # different sound than puck, would make it old quick

    def update(self, windowSize: list[int], deltaTime: float, soundHandler: sfx.SoundHandler) -> None:
        for player in self.board.players:
            self.friction(player, deltaTime)
            for puck in self.board.pucks:
                self.checkBounds(windowSize, puck, soundHandler)
                self.aabb(player, puck, soundHandler)