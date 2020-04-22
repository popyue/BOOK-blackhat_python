import socket
import sys

target_host = str(sys.argv[1])
target_port = int(sys.argv[2])

# Create socket object 
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send some data
client.sendto("AAaBBBCCC", (target_host,target_port))

# Receive some data
data,addr = client.recvfrom(4096)

print(data)
