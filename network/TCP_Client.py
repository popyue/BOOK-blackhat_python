import socket
import sys

#target_host="www.google.com"
#target_port=80

target_host=str(sys.argv[1])
target_port=int(sys.argv[2])

# Create socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Let client's connection connected 
client.connect((target_host,target_port))

# Send some data
client.send("GET / HTTP/1.1\r\nHost: google.com\r\n\r\n")

# Receive some data
reponse = client.recv(4096)

print(reponse)
