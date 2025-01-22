import socket, selectors
from collections import defaultdict

class ARserver:
    def __init__(self, name: str, ip="127.0.0.1", port=8000):
        self.name: str = name
        self.ip: str = ip
        self.port: int = port
        self.address: tuple[str, int] = (ip, port)
        self.selector: selectors.DefaultSelector = selectors.DefaultSelector()
        self.message_queues: dict[socket.socket, list[str]] = defaultdict(list)
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.codec: str = "utf-8"
        self.running: bool = False
        self.queue_size: int = 1024
        self.buffer_size: int = 1024

        self.command_prefix: str = "!"
        self.command_delimiter: str = "="

    def log_stdout(self, message: str) -> None:
        print(f"[ARSERVER-LOG] {self.name} | {message}\n")

    def startup(self):
        self.log_stdout(f"starting: {self.ip}:{self.port}")
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # allows server socket to be 're-bound'
        self.socket.bind((self.ip, self.port))
        self.socket.setblocking(False)
        self.socket.listen()
        self.selector.register(
            self.socket,
            selectors.EVENT_READ,
            self.handle_connection
        )
        self.running = True
        self.log_stdout(f"started: {self.ip}:{self.port}")

    def read_message(self, client_socket: socket.socket) -> str:
        try:
            message = client_socket.recv(self.buffer_size).decode(self.codec)
            if message:
                self.log_stdout(f"Message Received: {message}")
                return message
            return ""
        except Exception as e:
            self.log_stdout(f"Read Exception: {e}")
            return ""

    def write_message(self, client_socket: socket.socket, message: str) -> int:
        try:
            sent = 0
            while sent < len(message):
                sent += client_socket.send(message[sent:self.buffer_size].encode(self.codec))
            return sent
        except Exception as e:
            self.log_stdout(f"Write Exception: {e}")
            return 0

    def shout_message(self, client_socket: socket.socket, message: str):
        try:
            address = client_socket.getpeername()
            for client in self.message_queues.keys():
                if client != client_socket:
                    self.queue_message(client, f"[SHOUT] from ({address[0]}, {address[1]}): {message}")
        except Exception as e: self.log_stdout(f"broadcast message exception: {e}")

    def check_messages(self, client_socket: socket.socket) -> bool:
        try:
            if not self.message_queues[client_socket]:  # no more messages to send this client
                self.selector.modify(
                    client_socket,
                    selectors.EVENT_READ,
                    self.handle_client
                )
                return False
            return True
        except Exception as e:
            self.log_stdout(f"check message Exception: {e}")

    def get_message(self, client_socket: socket.socket) -> str:
        try:
            if self.message_queues[client_socket]:
                # send a response from the message queue
                return self.message_queues[client_socket].pop(0)
        except Exception as e:
            self.log_stdout(f"get message Exception: {e}")
            return ""

    def queue_message(self, client_socket: socket.socket, message: str) -> None:
        try:
            self.message_queues[client_socket].append(message)
            self.selector.modify(
                client_socket,
                selectors.EVENT_READ | selectors.EVENT_WRITE,
                self.handle_client
            )
        except Exception as e: self.log_stdout(f"queue message exception: {e}")

    def parse_message(self, client_socket: socket.socket, message: str):
        if message.startswith(self.command_prefix):
            #example 1: "!dc="
            #example 2: "!shout=Hello World!"
            
            if message.__contains__(self.command_delimiter):
                command, payload = map(str.strip, message[1:].split(self.command_delimiter))
            else:
                command = message[1:].strip()
                payload = ""

            # registered commands with callbacks
            if command == "sd":
                self.shutdown()
            if command == "dc":
                self.handle_disconnection(client_socket)
            if command == "list":
                client_list = ", ".join(str(s.getpeername()) for s in list(self.message_queues.keys()))
                self.queue_message(client_socket, f"connected: {client_list}")
            if command == "shout":
                self.shout_message(client_socket, payload)
        else:
            # server "default behavior" is to echo
            self.queue_message(client_socket, f"echo: {message}")

    def handle_connection(self, server_socket: socket.socket, mask: int):
        client_socket, client_address = server_socket.accept()
        client_socket.setblocking(False)
        self.message_queues[client_socket] = []
        self.selector.register(client_socket, selectors.EVENT_READ, self.handle_client)
        self.log_stdout(f"connected: {client_address}")
    
    def handle_disconnection(self, client_socket: socket.socket):
        address = client_socket.getpeername()
        self.message_queues.pop(client_socket, None)  # remove the message queue
        self.selector.unregister(client_socket)
        client_socket.close()
        self.log_stdout(f"disconnected: {address}")

    def handle_client(self, client_socket: socket.socket, mask: int):
        try:
            if mask & selectors.EVENT_READ:  # read events
                message = self.read_message(client_socket)
                self.parse_message(client_socket, message)

            if mask & selectors.EVENT_WRITE:  # write events
                if self.check_messages(client_socket):
                    message = self.get_message(client_socket)
                    self.write_message(client_socket, message)
        except Exception as e:
            self.log_stdout(f"handle client exception: {e}")
            self.handle_disconnection(client_socket)

    def run(self) -> None:
        while self.running:
            try:
                selection = self.selector.select(timeout=None)  # a blocking call
                for key, mask in selection:
                    callback = key.data  # the callback function to handle this selection
                    callback(key.fileobj, mask)
            except Exception as e: self.log_stdout(f"run exception: {e}")

    def shutdown(self) -> None:
        self.log_stdout("shutting down")
        for client in list(self.message_queues.keys()):
            self.handle_disconnection(client)
        self.selector.close()
        self.socket.close()
        self.running = False
        self.log_stdout("shut down")

if __name__ == "__main__":
    server = ARserver("Spider-Web")
    server.startup()
    server.run()
    server.shutdown()
