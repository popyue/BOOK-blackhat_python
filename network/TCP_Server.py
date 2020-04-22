import socket 
import threading 
import sys

bind_ip = str(sys.argv[1])
bind_port = int(sys.argv[2])

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip,bind_port))

server.listen(5)

print("[*] Lisening on %s:%d" % (bind_ip, bind_port))

# Handle the client's thread

def handle_client(client_socket):
    
    # Display data from client
    request = client_socket.recv(1024)

    print("[*] Received: %s" % request)

    # Send Back a Packet
    client_socket.send("ACK!!")
    client_socket.close()

while True:
    client,addr = server.accept()
    print("[*] Accepted connection from: %s:%d" % (addr[0],addr[1]))

    # Start up client thread to handle the receive data
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()
