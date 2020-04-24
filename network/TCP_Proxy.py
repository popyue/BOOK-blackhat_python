import sys
import socket 
import threading

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print("bind test\n")
        print("local_host: %s\n" %(local_host))
        print("locak_port: %d\n" %(local_port))
        server.bind((local_host, local_port))
    except:
        print("[!!] Failed to listen on %s:%d\n" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.\n")
        sys.exit(0)
    
    print("[*] Listening on %s:%d\n" % (local_host, local_port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # Display Host Connection Information
        print("[==>] Received incoming connection from %s:%d" % (addr[0], addr[1]))
        # Start a thread and remote communication
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()

def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: python TCP_Proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]\n")
        print("Example: python TCP_Proxy.py 127.0.0.1 000 10.12.132.1 9000 True\n")
        sys.exit(0)

    # Setting localhost sniffing information
    local_host = str(sys.argv[1])
    local_port = int(sys.argv[2])

    # Setting remote host information
    remote_host = str(sys.argv[3])
    remote_port = int(sys.argv[4])

    # let the proxy connect to remote host and receive data first
    # Then Send back to localhost

    receive_first = sys.argv[5]
    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    # Create the socket for sniffing 
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

def proxy_handler(client_socket, remote_host, remote_port, receive_first):

    # Connect to remote host
    remote_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    # If neccessary, receive data from remote host first
    if receive_first:
        print("test")
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        # Send receive_data to function which is responsible for dealing with response 
        remote_buffer = response_handler(remote_buffer)

        # if the data need to be sent bakc, the sent it back
        if len(remote_buffer):
            print("[<==] Sending %d bytes to localhost.\n" % len(remote_buffer))
            client_socket.send(remote_buffer)
    # Get into loop, and read from local host
    # And Send to remote host,send back o localhost
    # repeat repeat

    while True:

        # Read from local host
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            print("[==>] Received %d bytes from localhost.\n" % len(local_buffer))
            hexdump(local_buffer)

            # Send to the request handler function
            local_buffer = request_handler(local_buffer)

            # Send data to remote host
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote. \n")

        # Receive Response
        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote.\n" % len(remote_buffer))
            hexdump(remote_buffer)

            # Send to Reponse handler function
            remote_buffer = response_handler(remote_buffer)

            # Send Response back to localhost socket
            client_socket.send(remote_buffer)

            print("[<==] Sent to localhost! \n")
            
        # If there are no data between remote side and local side, the close the connection
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break 
# The following code is copy from
# http://code.activestate.com/recipes/142812-hex-dumper
# This code use to beautify the hex
def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in xrange(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append(b"%04X %-*s" %(i, length*(digits + 1), hexa, text))
        print(b'\n'.join(result))

def receive_from(connection):
    buffer = ""
    # Set timeout on 2 sec
    # You can adjust it according to your tester
    connection.settimeout(2)
    try:
        # Read buffer until data empty or timeout
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except:
        pass
    return buffer

def request_handler(buffer):
    # Do something modify in here
    # Modify packet / fuzzing test/ check authentication content
    return buffer

def response_handler(buffer): 
    # Do someting in here
    # modify packet / fuzzing / verify identification
    return buffer


#main()

if __name__ == '__main__':
    main()
