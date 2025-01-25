import d34dnet as dnet

class P2Client(dnet.inet.BaseClient):
    def __init__(self, username: str, location: list[float]):
        super().__init__()
        self.points: int = 0
        self.username: str = username
        self.playerid: str = "player"
        self.location: list[float] = location
        self.opponent_location: list[float] = [0.0, 0.0]

    def on_connect(self):
        self.log_stdout(f"pong2 client connected to server: {self.address}")
        self.write(self.build_request("info", {
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
            elif method == "relay":
                if self.playerid != response.get("params")["player_id"]:
                    self.opponent_location = response.get("params")["location"]
                    print(f"relayed player2 location: {self.opponent_location}")


