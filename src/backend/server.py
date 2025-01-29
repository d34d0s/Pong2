import pygame as pg
import d34dnet as dnet

# TODO: consider moving server-side code to the PBoard object as it already houses all the same info.

class Pong2Server(dnet.inet.BaseServer):
    def __init__(self):
        super().__init__(ip = "127.0.0.1", port = 8080)
        self.server_data: dict = {
            "players": dict()
        }
        self.players: dict = self.server_data["players"]
        # self.set_state("log-stdout", False)

    @dnet.inet.BaseServer.server_method
    def disconnect(self, endpoint, request) -> None:
        params = request.get("params")
        pong2id = params.get("pong2id")
        self._handle_disconnect(endpoint)

    def on_connect(self, endpoint):
        pong2id = f"p{len(self.connections)}"
        self.players[pong2id] = {"name": "pong2-player", "velocity": [0.0, 0.0], "location": [100.0, 100.0]}
        self.queue_response(endpoint.getpeername(),self.build_response("join", {"pong2id": pong2id}))

    def on_disconnect(self, endpoint):
        if not self.connections: self.stop()

    def on_read(self, endpoint, request) -> None:
        method = request.get("method")
        params = request.get("params")
        match method.lower():
            case "update":
                pong2id = params.get("pong2id")
                location = params.get("location")
                velocity = params.get("velocity")
                pucklocation = params.get("pucklocation")
                puckvelocity = params.get("puckvelocity")
                
                self.server_data["players"][pong2id]["location"] = location
                self.server_data["players"][pong2id]["velocity"] = velocity
                
                response = {k: v for (k, v) in self.players.items()}
                response["pucklocation"] = pucklocation
                response["puckvelocity"] = puckvelocity
                
                self.broadcast(self.build_response("update", response))

    def broadcast(self, response: dict) -> None:
        for addr in self.connections:
            self.queue_response(addr, response)

s = Pong2Server()
s.start()
s.run()
s.stop()

