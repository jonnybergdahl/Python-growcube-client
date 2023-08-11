import socket
import logging as logger
from growcube_client.growcubemessage import GrowcubeMessage


class GrowcubeSocketClient:

    DEFAULT_PORT = 8800

    def __init__(self, host: str, port: int):
        self.sock = None
        self.host = host
        self.port = port
        self.data = b''

    def connect(self):
        logger.debug("Connecting to %s:%i", self.host, self.port)
        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.settimeout(10)
            self.sock.connect((self.host, self.port))
            logger.info("Connected to %s:%i", self.host, self.port)
        except socket.error as ex:
            logger.error("Connect error: %s", ex)
            return False
        return True

    def is_connected(self):
        try:
            data = self.sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
            if len(data) == 0:
                return False
        except BlockingIOError:
            return True
        except ConnectionResetError:
            return False
        except Exception as e:
            logger.exception("unexpected exception when checking if a socket is closed")
            return False
        return True

    def disconnect(self):
        logger.info("Disconnecting")
        if self.sock is not None:
            self.sock.close()
        self.sock = None

    def send_message(self, message: str):
        logger.debug("Sending message %s", message)
        if not self.sock:
            raise ValueError('Not connected')
        message_bytes = message.encode('utf-8')
        self.sock.sendall(message_bytes)
        return True

    def receive_message(self):
        if not self.sock:
            raise ValueError('Not connected')

        #print(f"Current data: {self.data}")
        while True:
            # read from the socket
            try:
                data = self.sock.recv(32)
            except socket.timeout:
                #print("Timeout!")
                return None
            if not data:
                # no more data, return the message so far
                #print("no more data")
                return None
            # Remove all b'\x00' characters, seems to be used for padding?
            data = bytearray(filter(lambda c: c != 0, data))
            # add the data to the message buffer
            self.data += data
            # check if we have a complete message
            new_index, message = GrowcubeMessage.from_bytes(self.data)
            self.data = self.data[new_index:]

            if message is None:
                #print(f"Not complete data {self.data}")
                return None

            print(f"message: {message.command} - {message.payload}")
            # we have a complete message, remove consumed data
            return message

        return None

