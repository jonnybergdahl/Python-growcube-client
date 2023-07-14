# Not sure this will be of any use... 

import socket
import time

PORT_BROCAST = 9527

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server.settimeout(0.2)

message = b"crowcube"
server.sendto(message, ('<broadcast>', PORT_BROCAST))
print("message sent!")

