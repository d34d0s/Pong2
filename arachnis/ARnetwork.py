import socket

from .ARserver import ARserver

class ARnetwork:
    GLOBAL_DISCONNECT: str = "DISCONNECT"
    """ registered across ALL servers as the disconnect command """
    
    GLOBAL_CLEANUP: str = "CLEANUP"
    """ registered across ALL servers as the cleanup command (GLOBAL_DISCONNECT was recv) """
    
    GLOBAL_CLEAN: str = "CLEAN"
    """ registered across ALL servers as the clean command (GLOBAL_CLEANUP was recv) """

    def __init__(self, name: str="ARNetwork", ip: str="127.0.0.1"):
        self.name: str = name
        self.ip: str = ip
        self.codec: str = "utf-8"
        self.server_count: int = 0
        self.servers: dict[str, ARserver] = {}

    def log_stdout(self, message: str) -> None:
        print(f"[ARNETWORK-LOG] {self.name} | {message}\n")

    def make_server(self, server_name: str, server_port: int) -> None:
        try:
            server = ARserver(server_name, self.ip, server_port)
            server.startup()
            server.run()
            self.server_count += 1
            self.servers[server_name] = server
        except Exception as e: self.log_stdout(f"exception: {e}")

    def shout(self, message: str) -> None:
        """Send a message to all servers in the network."""
        try:
            for server in self.servers.values():
                server.broadcast(message)
        except Exception as e: self.log_stdout(f"exception: {e}")

    def kill_server(self, server_name: str) -> None:
        try:
            server = self.servers.pop(server_name)
            server.shutdown()
            self.server_count -= 1
        except Exception as e: self.log_stdout(f"exception: {e}")
