import d34dnet as dnet

class P2Server(dnet.inet.BaseServer):
    def __init__(self, ip = "127.0.0.1", port = 8080):
        super().__init__(ip, port)
        self.match_info: dict = {
            "player_max": 2,
            "player_count": 0,
            "player_info":  {}
        }

    def add_player(self, address: tuple[str, int], username: str, location: list[int], points: int) -> int:
        if self.match_info["player_count"] + 1 <= self.match_info["player_max"]:
            self.match_info["player_count"] += 1
            player_id = self.match_info["player_count"]
            self.match_info["player_info"][address] = {
                "id": player_id,
                "points": points,
                "location":  location,
                "username":  username
            }
        return self.match_info["player_count"]

    def relay_locations(self, endpoint) -> None:
        for address in self.connections:
            client = self.connections[address]["endpoint"]
            client_address = client.getpeername()
            if client != endpoint:
                self.queue_response(
                    client_address,
                    self.build_response(
                    "relay",
                    {
                    "player_id": self.match_info["player_info"][endpoint.getpeername()]["id"],
                    "location": self.match_info["player_info"][endpoint.getpeername()]["location"],
                }))

    def on_disconnect(self, endpoint):
        if self.match_info["player_count"] - 1 < 0:
            self.match_info["player_count"] = 0
        else:
            self.match_info["player_count"] -= 1

    @dnet.inet.BaseServer.server_method
    def info(self, endpoint, request) -> None:
        # info request should look like: {... "method": "info", "params": {"points": 0, "location": [0.0, 0.0], "username": "pong2-beast"}}
        info = request.get("params")
        address = endpoint.getpeername()
        points, location, username = list(info.values())
        player_id = self.add_player(address, username, location, points)
        self.log_stdout(f"player info recieved from {address}: (user){username} | (points){points} | (loc){location}")
        
        address = endpoint.getpeername()
        self.queue_response(address, self.build_response("info", {"player_id": f"{player_id}"}))

    @dnet.inet.BaseServer.server_method
    def move(self, endpoint, request) -> None:
        # move request should look like: {... "method": "move", "params": [100, 100]}
        # this sets a player's position to 100, 100 on the server
        # the server should then relay the new server state to other players
        try:
            address = endpoint.getpeername()
            
            location = request.get("params")
            self.match_info["player_info"][address]["location"] = location
            
            self.log_stdout(f"{address} move to: {location}")
            self.log_stdout(f"player info: {self.match_info}")
            self.relay_locations(endpoint)
        except KeyError as e:
            self.log_stdout(f"invalid move parameters!")

pserver = P2Server()
pserver.start()
pserver.run()
pserver.stop()