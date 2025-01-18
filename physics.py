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
        
    def aabb(self, player: pBar.PBar, puck, deltaTime: float) -> None:
        if puck.velocity[0] > 0:
            if puck.rect.colliderect(player.rect):
                overlap = player.rect.left - puck.rect.right
                puck.location[0] += overlap
                puck.velocity[0] = -puck.speed
                puck.velocity[1] += (player.velocity[1] / 4)
                
                player.location[0] -= overlap

        elif puck.velocity[0] < 0:
            if puck.rect.colliderect(player.rect):
                overlap = player.rect.right - puck.rect.left
                puck.location[0] += overlap
                puck.velocity[0] = puck.speed
                puck.velocity[1] = (player.velocity[1] / 4)
                
                player.location[0] -= overlap

    def checkBounds(self, windowSize: list[int], puck: pPuck.PPuck) -> None:
        # puck top bounce
        if puck.velocity[1] < 0 and (puck.location[1] + 1) < 0:
            puck.velocity[1] = puck.speed
            puck.location[1] = 0
        if puck.velocity[1] > 0 and ((puck.location[1] + puck.size[1]) + 1) > windowSize[1] - puck.size[1]:
            puck.velocity[1] = -puck.speed
            puck.location[1] = windowSize[1] - puck.size[1]

    def update(self, windowSize: list[int], deltaTime: float) -> None:
        for player in self.board.players:
            self.friction(player, deltaTime)
            for puck in self.board.pucks:
                self.checkBounds(windowSize, puck)
                self.aabb(player, puck, deltaTime)
