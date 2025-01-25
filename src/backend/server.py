import d34dnet as dnet

class P2Server(dnet.inet.BaseServer):
    def __init__(self, ip = "127.0.0.1", port = 8080):
        super().__init__(ip, port)
        self.match_info: dict = {
            "player_max": 2,
            "player_count": 0,
            "player_info":  {}
        }

    def add_player(self, username: str, location: list[int], points: int) -> int:
        if self.match_info["player_count"] + 1 <= self.match_info["player_max"]:
            self.match_info["player_count"] += 1
            player_id = self.match_info["player_count"]
            self.match_info["player_info"][f"player{player_id}"] = {
                "points":points,
                "location": location,
                "username": username
            }
        return self.match_info["player_count"]

    @dnet.inet.BaseServer.server_method
    def info(self, endpoint, request) -> None:
        # info request should look like: {... "method": "info", "params": {"points": 0, "location": [0.0, 0.0], "username": "pong2-beast"}}
        params = request.get("params")
        points, location, username = list(params.values())
        player_id = self.add_player(username, location, points)
        self.log_stdout(f"player info recieved: (user){username} | (points){points} | (loc){location}")
        
        address = endpoint.getpeername()
        self.queue_response(address, self._build_response("info", {"player_id": f"player{player_id}"}))

    @dnet.inet.BaseServer.server_method
    def move(self, endpoint, request) -> None:
        # move request should look like: {... "method": "move", "params": {"player1": [100, 100]}}
        # this sets player 1's position to 100, 100 on the server
        # the server should then send the new 'positions' server state to player 2
        try:
            params = request.get("params")
            player = list(params.keys())[0]

            self.match_info["player_info"][player]["location"] = params[player]
            
            self.log_stdout(f"{player} move to: {params[player]}")
            self.log_stdout(f"player info: {self.match_info}")
        except KeyError as e:
            self.log_stdout(f"invalid move parameters!")

pserver = P2Server()
pserver.start()
pserver.run()
pserver.stop()