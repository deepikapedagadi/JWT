#app and check 
import socket
s_socket=socket.socket()
s_socket.bind(('localhost',1000))
s_socket.listen(1)

print("server is listening ")
conn,add=s_socket.accept()
print("Connected to ",add)
while True:
    data=conn.recv(1024).decode()
    if not data:
        break
    print("client data is ",data)
    conn.send(f"received data is{data}".encode() )

conn.close()