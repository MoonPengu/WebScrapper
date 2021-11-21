# My computer IP Address and hostname
import socket

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
print("My Computer Name is:" + hostname)
print("My Computer IP Address is:" + IPAddr)

# Fetch IP of any website
import socket as s

try:
    host = input("Please enter the hostname you want the ip for : ")
    print(f'IP of {host} is {s.gethostbyname(host)}')
except Exception as e:
    print('Failed to resolve IP: ', e)
