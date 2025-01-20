import json, types, collections, selectors, socket, threading

"""
pongNet message protocol
message: dict = {"cmd": "", data: {}}

server command callbacks must be prefixed with `on` (e.g. onDelete, onMovement, onDisconnect)
server command callbacks must specify params for the message data and server state (e.g. onCmd(data=None, state=None))

# example move callback for a `move` command
# the callback accepts the message data containing the client's location
# and the server state where positions are stored
# the callback then updates the server state
def onMove(data, state) -> None:
    state["positions"][int(data["playerID"])] = data["position"]

TODO parseMessage() method for issuing serverCommand() calls and passing message data and server state to the callback
TODO default server command `broadcast` used to send out server state to all connected clients

"""

PNetAddress: collections.namedtuple = collections.namedtuple("PNetAddress", ["ip", "port"])
PNetCallback: collections.namedtuple = collections.namedtuple("PNetCallback", ["cmd", "callback"])

class PServer:
    class state:
        customState = None
        running: bool = False
        commandCount: int = 0
        connectionCount: int = 0
        commands: dict[str, callable] = {}
        connections: list[socket.socket] = []

    class info:
        name: str = "PServer"
        commandMax: int = 255
        bufferSize: int = 1024
        encoding: str = "utf-8"
        connectionMax: int = 1024
        defaultTimeout: int = 1000
        address: tuple[str, int] = ("", 0)

    def __init__(self, name: str, ip: str, port: int, customState=None):
        self.info.name = str(name)
        self.info.address = PNetAddress(ip=ip, port=port)

        self.state.customState = customState

        self.selector = selectors.DefaultSelector()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def startup(self) -> None:
        self.state.running = True
        self.socket.bind(self.info.address)
        self.socket.listen()
        self.selector.register(self.socket, selectors.EVENT_READ, data=self.state.customState)

        # register default commands
        self.registerCommand("disconnect", lambda state: state)

    def buildMessage(self, cmd: str, data: dict) -> dict:
        return {"cmd": cmd, "data": data}

    def registerCommand(self, cmd: str, callback: callable) -> None:
        if (self.state.commandCount + 1) <= self.info.commandMax:
            try:
                self.state.commands[cmd] = PNetCallback(cmd=cmd, callback=callback)
                self.state.commandCount += 1
                print(f"Server Command Registered: {cmd}")
            except Exception as e:
                print(f"Server Exception: {e}")
    
    def serverCommand(self, cmd: str) -> None:
        try:
            callback = self.state.commands[cmd]
            callback.callback(self.state.customState)
            print(f"Server Command Called: {callback.cmd}")
        except Exception as e:
            print(f"Server Exception: {e}")

    def unregisterCommand(self, cmd: str) -> None:
        try:
            callback = self.state.commands.pop(cmd)
            self.state.commandCount -= 1
            print(f"Server Command Un-Registered: {callback.cmd}")
        except Exception as e:
            print(f"Server Exception: {e}")

    def handleConnect(self, key, mask) -> None:
        if (self.state.connectionCount + 1) <= self.info.connectionMax:
            data = key.data
            sock = key.fileobj
            if isinstance(sock, socket.socket):
                try:

                    conn, addr = sock.accept()
                    if conn is not None:
                        print(f"Server Connection: {addr}")
                        conn.setblocking(False)
                        self.selector.register(
                            conn,
                            events=selectors.EVENT_READ|selectors.EVENT_WRITE,
                            data=types.SimpleNamespace(clientid=self.state.connectionCount)
                        )
                        self.state.connections.append(conn)
                        self.state.connectionCount += 1
                except Exception as e:
                    print(f"(HANDLE CONNECT) Server Exception: {e}")
    
    def handleRead(self, key, mask) -> dict:
        try:
            data = key.data
            sock = key.fileobj
            if not isinstance(sock, socket.socket): return {"cmd": "", "data": {}}

            message = sock.recv(self.info.bufferSize)
            if message is None: return {"cmd": "", "data": {}}
            
            decoded = json.loads(message.decode(self.info.encoding))
            print(f"Server Read: {decoded}")
            return message
        except Exception as e:
            print(f"(HANDLE READ) Server Exception: {e}")
            return {"cmd": "", "data": {}}

    def handleWrite(self, key, mask, message: dict) -> int:
        try:
            data = key.data
            sock = key.fileobj
            if not isinstance(sock, socket.socket): return 0

            encoded = json.dumps(message).encode(self.info.encoding)
            print(f"Server Write: {message} to {sock.getpeername()}")

            sent = 0
            while sent < len(message):
                sent = sock.send(encoded[sent:])
            return sent
        except Exception as e:
            print(f"(HANDLE WRITE) Server Exception: {e}")
            return 0

    def handleDisconnect(self, key, mask) -> None:
        try:
            data = key.data
            sock = key.fileobj
            if not isinstance(sock, socket.socket): return
            
            self.selector.unregister(sock)
            self.state.connections.remove(sock)
            self.state.connectionCount -= 1
            # send disconnect command to close client socket
            self.handleWrite(key, mask, {"cmd": "disconnect", "data": {}})

        except Exception as e:
            print(f"(HANDLE DISCONNECT) Server Exception: {e}")

    def handleClient(self, key, mask) -> None:
        try:
            if (mask & selectors.EVENT_READ) == selectors.EVENT_READ:
                message = self.handleRead(key, mask)
            if (mask & selectors.EVENT_WRITE) == selectors.EVENT_WRITE:
                self.handleWrite(key, mask, self.buildMessage("cmd", {}))
        except Exception as e:
            print(f"(HANDLE CLIENT) Server Exception: {e}")

    def run(self) -> None:
        try:
            while self.state.running:
                selection = self.selector.select(timeout=self.info.defaultTimeout)
                for key, mask in selection:
                    if key.data == self.state.customState:
                        self.handleConnect(key, mask)
                    else:
                        self.handleClient(key, mask)
        except Exception as e:
            print(f"(RUN) Server Exception: {e}")
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        self.state.running = False
        self.selector.close()
        for s in self.state.connections:
            self.selector.unregister(s)
            s.close()
        self.socket.close()


class PClient:
    class state:
        running: bool = False

    class info:
        bufferSize: int = 1024
        encoding: str ="utf-8"
        address: tuple[str, int] = ("", 0)

    def __init__(self, name: str, ip: str, port: int):
        self.info.ip = ip
        self.info.port = port
        self.info.address = PNetAddress(ip, port)
        
        self.selector = selectors.DefaultSelector()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def startup(self) -> None:
        self.state.running = True
        self.socket.connect_ex(self.info.address)
        self.selector.register(self.socket, events=selectors.EVENT_READ|selectors.EVENT_WRITE, data=types.SimpleNamespace(clientid=12345))

    def buildMessage(self, cmd: str, data: dict) -> dict:
        return {"cmd": cmd, "data": data}

    def handleRead(self, key, mask) -> dict:
        try:
            data = key.data
            sock = key.fileobj
            if not isinstance(sock, socket.socket): return {"cmd": "", "data": {}}

            message = sock.recv(self.info.bufferSize)
            if message is None: return {"cmd": "", "data": {}}
            
            decoded = json.loads(message.decode(self.info.encoding))
            print(f"Client Read: {decoded}")
            return message
        except Exception as e:
            print(f"(HANDLE READ) Client Exception: {e}")
            return {"cmd": "", "data": {}}

    def handleWrite(self, key, mask, message: dict) -> int:
        try:
            data = key.data
            sock = key.fileobj
            if not isinstance(sock, socket.socket): return 0

            encoded = json.dumps(message).encode(self.info.encoding)
            print(f"Client Write: {message} to {sock.getpeername()}")

            sent = 0
            while sent < len(message):
                sent = sock.send(encoded[sent:])
            return sent
        except Exception as e:
            print(f"(HANDLE WRITE) Client Exception: {e}")
            return 0

    def handleClient(self, key, mask) -> None:
        try:
            if (mask & selectors.EVENT_READ) == selectors.EVENT_READ:
                message = self.handleRead(key, mask)
            if (mask & selectors.EVENT_WRITE) == selectors.EVENT_WRITE:
                self.handleWrite(key, mask, self.buildMessage("move", {"playerID": 0, "position": [123.0, 456.0]}))
        except Exception as e:
            print(f"(HANDLE CLIENT) Client Exception: {e}")

    def run(self) -> None:
        try:
            while self.state.running:
                selection = self.selector.select(timeout=None)
                for key, mask in selection:
                    if key.data is None: pass
                    else:
                        self.handleClient(key, mask)
        except Exception as e:
            print(f"(RUN) Client Exception: {e}")
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        self.state.running = False
        self.selector.close()
        self.socket.close()

