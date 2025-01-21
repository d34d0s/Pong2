import socket, selectors

class ARclient:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.codec: str = "utf-8"
        self.running: bool = True
        self.connected: bool = False
        self.buffer_size: int = 1024
        self.server: tuple[str, int] = None
        self.address: tuple[str, int] = None
        self.selector: selectors.DefaultSelector = selectors.DefaultSelector()
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def log_stdout(self, message: str) -> None:
        print(f"[CLIENT-LOG] {self.name} | {message}\n")

    def read_state(self) -> None: ...
    def write_state(self) -> None: ...
    
    def parse_message(self, message: str) -> str | None:
        """
        this function parses messages to the server
        comparing the header against registered server commands
        the the author client socket and message payload are then passed as a command parameters.
        """
        try:
            if message.lower() == "!dc":
                # server closed our connection
                self.disconnect()

        except Exception as e: self.log_stdout(f"Exception: {e}")

    def read_message(self) -> None:
        if self.connected and isinstance(self.socket, socket.socket):
            try:
                message = self.parse_message(self.socket.recv(self.buffer_size).decode(self.codec))
                self.log_stdout(f"Message Recieved: {message}")
            except Exception as e: self.log_stdout(f"Exception: {e}")

    def write_message(self, message: str) -> int:
        if self.connected and isinstance(self.socket, socket.socket):
            try:
                sent = 0
                while sent < len(message):  # ensure every byte is sent (blocking)
                    sent = self.socket.send(message[sent:self.buffer_size].encode(self.codec))
                return sent
            except Exception as e:
                self.log_stdout(f"Exception: {e}")
                return 0

    def call_command(self) -> None:
        if self.connected and isinstance(self.socket, socket.socket):
            try: pass
            except Exception as e: self.log_stdout(f"Exception: {e}")

    def connect(self, ip: str, port: int) -> None:
        if self.connected: pass
        self.server = (ip, port)
        self.socket.connect_ex(self.server)
        self.address = self.socket.getpeername()
        self.selector.register(self.socket, selectors.EVENT_READ | selectors.EVENT_WRITE, None)
        self.log_stdout(f"Connected To: {self.server}")

    def disconnect(self) -> None:
        if self.connected:
            try:
                self.log_stdout(f"Disconnected From: {self.server}")
                self.selector.unregister(self.socket)
                self.socket.close()
                self.server = None
                self.address = None
                self.connected = False
            except Exception as e: self.log_stdout(f"Exception: {e}")

    def run(self) -> None:
        if self.running:
            try:
                while self.running:
                    # TODO: remove this test
                    self.write_message("Hello, Server!")
                    # self.write_message(input(f"{self.server} >: "))
                    # self.shutdown()
            except Exception as e:
                self.log_stdout(f"Main Loop Exception (SHUTTING DOWN): {e}")
                self.shutdown()
    
    def shutdown(self) -> None:
        if self.running == True:
            self.disconnect()
            self.running = False

c = ARclient("BugZapper001")
c.connect("127.0.0.1", 8000)
c.run()
c.disconnect()