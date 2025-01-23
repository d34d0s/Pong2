import json, socket, threading

class ARclient:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.codec: str = "utf-8"
        self.running: bool = True
        self.buffer_size: int = 1024

        self.connected: bool = False
        self.address: tuple[str, int] = None
        self.server_address: tuple[str, int] = None

        self.thread_lock: threading.Lock = threading.Lock()
        self.read_thread: threading.Thread = None   # ARclient is dual-threaded leaving writes to block the main thread
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # allows client socket to be 're-bound'

    def log_stdout(self, message: str) -> None:
        print(f"[ARCLIENT-LOG] {self.name} | {message}\n")

    def read_message(self) -> None:
        while self.running:
            if self.connected:
                try:
                    message = self.socket.recv(self.buffer_size).decode(self.codec)
                    if message: self.log_stdout(f"message read: {message}")
                except Exception as e: self.log_stdout(f"read exception: {e}")

    def write_message(self, message: str) -> int:
        if self.connected:
            try:
                sent = 0
                while sent < len(message):
                    sent += self.socket.send(message[sent:self.buffer_size].encode(self.codec))
                self.log_stdout(f"message written: '{message}({sent}bytes)'")
                return sent
            except Exception as e:
                self.log_stdout(f"write Exception: {e}")
                return 0

    def connect(self, ip: str="127.0.0.1", port: int=8000) -> None:
        if not self.connected:
            try:
                self.server_address = (ip, port)
                self.socket.connect(self.server_address)
                self.address = self.socket.getpeername()

                self.read_thread = threading.Thread(target=self.read_message, daemon=True)
                self.read_thread.start()
                
                with self.thread_lock:
                    self.connected = True
                self.thread_lock.release()
                
                self.log_stdout(f"connected: {self.server_address}")
            except Exception as e: self.log_stdout(f"exception: {e}")

    def reconnect(self) -> None:
        try:
            if self.connected:
                self.log_stdout(f"reconnecting...")
                
                address = self.server_address
                self.disconnect()

                self.connect(address[0], address[1])
                self.log_stdout(f"reconnected...")
        except Exception as e:
            self.log_stdout(f"reconnect exception: {e}")

    def disconnect(self) -> None:
        if self.connected:
            try:
                address = self.server_address
                self.log_stdout(f"disconnecting: {address}")

                self.socket.close()
                self.read_thread.join(timeout=2.0)
                
                self.address = None
                self.server_address = None
                
                with self.thread_lock:
                    self.connected = False
                self.thread_lock.release()
                
                self.log_stdout(f"disconnected: {address}")
            except Exception as e: self.log_stdout(f"exception: {e}")

    def run(self) -> None:
        try:
            while self.running:
                if self.connected:
                    message = input(">: ").strip()
                    if message: self.write_message(message)
        except Exception as e: self.log_stdout(f"run exception: {e}")

    def shutdown(self) -> None:
        if self.running:
            self.log_stdout("shutting down")
            self.disconnect()
            self.running = False
            self.log_stdout("shut down")

if __name__ == "__main__":
    client = ARclient("Bug-Zapper")
    client.connect()
    client.run()
    client.shutdown()
