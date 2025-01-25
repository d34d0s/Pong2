import d34dnet as dnet

class P2Client(dnet.inet.BaseClient):
    def __init__(self, username: str, location: list[float]):
        super().__init__()
        self.points: int = 0
        self.location: list[float] = location
        self.username: str = username
        self.playerid: str = "player"

    def on_connect(self):
        self.log_stdout(f"pong2 client connected to server: {self.address}")
        self._write(self.build_request("info", {
            "points": self.points,
            "location": self.location,
            "username": self.username
        }))
    
    def on_read(self, response):
        method = response.get("method", None)
        if method:
            if method == "info":
                self.playerid = response.get("params")["player_id"]
                self.log_stdout(f"playerid set: {self.playerid}")

