import sys
import socket
import getopt
import threading 
import subprocess

# Define Global Variable 
listen  = False
command = False
upload  = False
execute = ""
target  = ""
upload_destination  = ""
port    = 0

def usage():
    print("Create a netcat by python!!\n")
    print("")
    print("Usage: netcat.py -t target_host -p port\n")
    print("-l --listen      :sniffing on [host]:[port] and connect to it\n")
    print("-e --execute=file_to_run     :Connect created, execute specific file\n")
    print("-c --command     :start command line shell\n")
    print("-u --upload=destination      :Connect created, upload file and display [destination]\n")
    print("")
    print("EXAMPLE: \n")
    print("netcat.py -t 192.168.0.1 -p 5555 -l -c\n")
    print("netcat.py -t 192.168.0.1 -p 5555 -l u=c:\\target.exe\n")
    print("netcat.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"\n")
    print("echo 'ABCDEFG' | ./netcat.py -t 192.168.11.12 -p 135\n")
    sys.exit(0)

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()
    
    # Scan Command
    try:
        opts,args = getopt.getopt(sys.argv[1:],"hle:t:p:cu", ["help","listen","eexecute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
    
    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--command"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Option does not handle!!\n"
            usage()
    # Sniffing or send data from stdin
    if not listen and len(target) and port >0:

        # Read buffer from command
        # This will block command, so press CTRL-D if you don;t want to send data from stdin

        buffer = sys.stdin.read()
        # Send data 
        client_sender(buffer)

    # Sniffing code block
    # At the same time, it may upload, execute or use shell with other option

    if listen:
        server_loop()

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to Target Host
        client.connect((target,port))

        if len(buffer):
            client.send(buffer)

        while True:

            # Wait for data send back
            recv_len = 1
            response = ""
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break
            print(response)

            # Wait for more input
            buffer = raw_input("")
            buffer += "\n"

            # Send
            client.send(buffer)
    except:
        print("[*] Exception! Exiting.")

        # close connection
        client.close()

def server_loop():
    global target

    # If defination does not set, sniffing all interface
    if not len(target):
        target = "0.0.0.0"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        # Start up a thread to deal with all new client
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def run_command(command):
    # strip line command(\n)
    command = command.rstrip()

    # Execute command and get output
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Command execute FAILED !! \r\n"

    # Send Output to client
    return output

def client_handler(client_socket):
    global upload
    global execute 
    global command

    # check upload
    if len(upload_destination):

        # Read all bytes and write to specify location
        file_buffer = ""

        # Read until no data 
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data
        # Try to save data to file
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
            
            # Program Response Data Saved Successful
            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)
    # Check command
    if len(execute):

        # Command Execution
        output = run_command(execute)

        client_socket.send(output)
    # If request shell command, get into other loop
    if command:

        while True:
            # Display a easy hint
            client_socket.send("<netcat:#> ")

            # Continuing receive data, until get LF (Enter)
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
            # Get command output
            response = run_command(cmd_buffer)

            # Response
            client_socket.send(response)

if __name__ == '__main__':
    main()

