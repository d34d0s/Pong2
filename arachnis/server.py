import socket, selectors

class ARserver:
    def __init__(self, name: str, ip: str, port: int) -> None:
        self.name: str = name
        self.codec: str = "utf-8"
        self.running: bool = False
        self.queue_size: int = 0
        self.buffer_size: int = 1024
        self.address: tuple[str, int] = (ip, port)
        self.selector: selectors.DefaultSelector = selectors.DefaultSelector()
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def log_stdout(self, message: str) -> None:
        print(f"[SERVER-LOG] {self.name} | {message}\n")

    def read_state(self) -> None: ...
    def write_state(self) -> None: ...

    def parse_message(self, mask: int, client: socket.socket, message: str) -> str:
        """
        this function parses messages to the server
        comparing the header against registered server commands
        the the author client socket and message payload are then passed as a command parameters.
        """
        print(f"MESSAGE TO PARSE {message}")
        try:
            if message.lower() == "?dc":
                # client issued server close command
                # default close command will send back a `closed` message for the client to close its connection
                self.write_message(mask, client, "!dc")
            return message
        except Exception as e:
            self.log_stdout(f"Exception: {e}")
            return ""

    def read_message(self, mask: int, client: socket.socket) -> None:
        if (mask & selectors.EVENT_READ) == selectors.EVENT_READ and isinstance(client, socket.socket):
            try:
                message = self.parse_message(mask, client, client.recv(self.buffer_size).decode(self.codec))
                self.log_stdout(f"Message Recieved: {message}")
            except Exception as e: self.log_stdout(f"Exception: {e}")

    def write_message(self, mask: int, client: socket.socket, message: str) -> int:
        if (mask & selectors.EVENT_WRITE) == selectors.EVENT_WRITE and isinstance(client, socket.socket):
            try:
                sent = 0
                while sent < len(message):  # ensure every byte is sent (blocking)
                    sent = client.send(message[sent:self.buffer_size].encode(self.codec))
                return sent
            except Exception as e:
                self.log_stdout(f"Exception: {e}")
                return 0
    
    def register_command(self) -> None: ...
    def call_command(self) -> None: ...
    def unregister_command(self) -> None: ...

    def handle_connection(self, key, mask: int) -> None:
        try:
            client, address = key.fileobj.accept()
            self.log_stdout(f"Connection: {address[0]}:{address[1]}")
            self.selector.register(client, selectors.EVENT_READ | selectors.EVENT_WRITE, "client-connection")
        except Exception as e: self.log_stdout(f"Exception: {e}")

    def service_connection(self, key, mask: int) -> None:
        try:
            data = key.data
            client = key.fileobj
            # TODO: (remove this test) spawn a daemon thread for the read_message method to run on
            self.read_message(mask, client)
        except Exception as e: self.log_stdout(f"Exception: {e}")

    def startup(self) -> None:
        if self.running == False:
            self.running = True
            self.socket.bind(self.address)
            self.socket.listen(self.queue_size)
            self.selector.register(self.socket, selectors.EVENT_READ | selectors.EVENT_WRITE, None)
            self.log_stdout(f"Listening On: {self.address[0]}:{self.address[1]}")

    def maintenance(self) -> None:
        if self.running: pass

    def run(self) -> None:
        if self.running:
            try:
                while self.running:
                    selection = self.selector.select(timeout=None)
                    for key, mask in selection:
                        if key.data is None: self.handle_connection(key, mask)
                        else: self.service_connection(key, mask)
            except Exception as e:
                self.log_stdout(f"Main Loop Exception (SHUTTING DOWN): {e}")
                self.shutdown()

    def shutdown(self) -> None:
        if self.running == True:
            self.socket.close()
            self.selector.close()
            self.running = False

s = ARserver("Spider", "127.0.0.1", 8000)
s.startup()
s.run()
s.shutdown()
