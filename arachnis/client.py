import socket
import threading

class ARclient:
    def __init__(self, host='127.0.0.1', port=8000):
        self.running = True
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def log_stdout(self, message: str) -> None:
        print(f"[ARCLIENT-LOG] {self.name} | {message}\n")

    def connect(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print(f"[CLIENT] Connected to {self.host}:{self.port}")
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.send_messages()
        except ConnectionRefusedError:
            print("[CLIENT] Failed to connect. Is the server running?")
            self.running = False

    def receive_messages(self):
        try:
            while self.running:
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    print("[CLIENT] Server closed the connection.")
                    self.running = False
                    break
                print(f"[CLIENT] Received: {message}")
        except ConnectionResetError:
            print("[CLIENT] Connection reset by server.")
        finally:
            self.client_socket.close()

    def send_messages(self):
        try:
            while self.running:
                message = input("> ")
                if message.lower() == "!dct":
                    print("[CLIENT] Disconnecting...")
                    self.running = False
                    break
                self.client_socket.sendall(message.encode('utf-8'))
        except Exception:
            print("[CLIENT] Unable to send message. Connection is closed.")
        finally:
            self.client_socket.close()

if __name__ == "__main__":
    client = ARclient()
    client.connect()
