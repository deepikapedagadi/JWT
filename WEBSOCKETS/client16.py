#app and check
import socket
c_socket=socket.socket()
c_socket.connect(('localhost',1000))

while True:
    msg=input("You:")
    c_socket.send(msg.encode())
    res=c_socket.recv(1024).decode()
    print("server:",res)