import socket
import ipaddress
from typing import Dict


def scan(ip, from_port, to_port, udp):
	min_port = 0 
	max_port = 65535
	result = dict()
	addr = ipaddress.ip_address(ip)
	#print(addr)
	if addr.version == 4:
		if from_port < min_port or from_port > max_port:
			return result
		if to_port < min_port or to_port > max_port:
			return result
		if udp == False:
			#print(false)
			for port in range(from_port, to_port+1):
				try:
					with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
						sock.settimeout(0.8)
						if not sock.connect_ex((ip,port)):
							print(s.recvfrom(port))
							result.update({port: True})
						else:
							result.update({port: False})
				except Exception:
					return False
		else:
			for port in range(from_port, to_port+1):
				try:
					with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
						s.settimeout(0.8)
						if not s.connect_ex((ip,port)):
							print(s.recvfrom(port))
							result.update({port: True})
						else:
							result.update({port: False})
				except Exception:
					return False
		print('result:',result)
	else:
		return {}

def main():
	ip = '127.0.0.1'
	from_port = 9778
	to_port = 9779
	'''
	ip = input("IP Address is :")
	from_port = int(input("Port number start:"))
	to_port = int(input("Port number end:"))
	'''
	udp = eval(input("True or False:"))
	print(udp)
	scan(ip, from_port, to_port, udp)


if __name__ == '__main__':
	main()