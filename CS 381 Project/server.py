import threading
import socket
import sqlite3

#connect to database/ create 
conn = sqlite3.connect('chatroom.db')
c = conn.cursor()

#messages table 
c.execute('''CREATE TABLE IF NOT EXISTS messages
             (name TEXT, message TEXT)''')

host = '127.0.0.1'
port = 59000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
names = []

def broadcast(message, name):
    for client in clients:
        client.send(message)
    conn = sqlite3.connect('chatroom.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages VALUES (?, ?)", (name, message))
    conn.commit()
    conn.close()

def handle_client(client):
    while True:
        try: 
            message = client.recv(1024)
            name = names[clients.index(client)]
            if message:
                broadcast(message, name)
        except ConnectionResetError:
            index = clients.index(client)
            name = names[index]
            clients.remove(client)
            client.close()  # Close the socket associated with the disconnected client
            names.remove(name)
            broadcast(f'{name} has left the chatroom'.encode('utf-8'), name)
            break

#main function fore client connection 
def receive():
    while True:
        print('Server is running...')
        client, address = server.accept()
        print(f'connection is established with {str(address)}')
        client.send('name?'.encode('utf-8'))
        name = client.recv(1024)
        names.append(name)
        clients.append(client)
        print(f'The nickname of this client is: {name}'.encode('utf-8'))
        broadcast(f'{name} has entered the chat.'.encode('utf-8'), name) 
        client.send('You have connected!'.encode('utf-8'))
        thread = threading.Thread(target = handle_client, args =(client,))
        thread.start()

if __name__ == "__main__":
    receive()
