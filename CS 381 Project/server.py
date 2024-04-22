import threading
import socket
import sqlite3

#create and connect to database
conn = sqlite3.connect('chatroom.db')
c = conn.cursor()

#messages table 
c.execute('''CREATE TABLE IF NOT EXISTS messages
             (name TEXT, message TEXT)''')

# define host and port 
host = '127.0.0.1'
port = 59000

# server socket 
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# lists to keep track of clients/names 
clients = []
names = []

#encryption function- Caesar's cipher 
def encrypt(message, key):
    encrypted_message = ""
    for char in message:
        if char.isalpha():
            #shift character by specified key, in this case always 3 
            shifted = ord(char) + key
            #case for diff cases and wrapping around the alphabet 
            if char.islower():
                if shifted > ord('z'):
                    shifted -= 26
                elif shifted < ord('a'):
                    shifted += 26
            elif char.isupper():
                if shifted > ord('Z'):
                    shifted -= 26 
                elif shifted < ord('A'):
                    shifted += 26
            encrypted_message += chr(shifted)
        else: 
            #special characters remain unchanged 
            encrypted_message += char
    #print(encrypted_message, "encrypted")
    #returns encrypted message 
    return encrypted_message

#decryption function follows same logic as the original encryption function 
def decrypt(encrypted_message, key):
    decrypted_message = ""
    for char in encrypted_message:
        if char.isalpha():
            shifted = ord(char) - key
            if char.islower():
                if shifted < ord('a'):
                    shifted += 26
            elif char.isupper():
                if shifted < ord('A'):
                    shifted += 26 
            decrypted_message += chr(shifted)
        else: 
            #special characters remain the same 
            decrypted_message += char
    #print(decrypted_message, "decrypted")
    return decrypted_message

#broadcast so all clients can see each message if 'online' 
def broadcast(message, name):
    for client in clients:
        #encrypt the message BEFORE broadcasting 
        encrypted_message = encrypt(f'{message}', 3)
        #proceed to send encrypted message 
        client.send(encrypted_message.encode('utf-8'))
    #necessary to keep threading for each instance 
    conn = sqlite3.connect('chatroom.db')
    c = conn.cursor()
    
    #insert into database 
    c.execute("INSERT INTO messages VALUES (?, ?)", (name, message))
    conn.commit()
    conn.close()

# handle each clients messages 
def handle_client(client):
    #continuously receive & process messages from the client 
    while True:
        try:
            encrypted_message = client.recv(1024)
            #decrypt message, get the client's name, and broadcast 
            if not encrypted_message:
                continue
            name = names[clients.index(client)]
            decrypted_message = decrypt(encrypted_message.decode('utf-8'), 3)  # Decrypt the message
            if decrypted_message:
                broadcast(decrypted_message, name)
        except ConnectionResetError:
            #remove client if disconnected and close socket 
            index = clients.index(client)
            name = names[index]
            clients.remove(client)
            client.close()  # Close the socket associated with the disconnected client
            names.remove(name)
            broadcast(f'{name} has left the chatroom'.encode('utf-8'), name)
            break


#main function for client connection 
def receive():
     
    while True:
        print('Server is running...')
        client, address = server.accept() #continuously accept new connections from client
        print(f'connection is established with {str(address)}')
        client.send('name?'.encode('utf-8'))
        #receive client info and add to lists 
        name = client.recv(1024)
        names.append(name)
        clients.append(client)

        #broadcast each entry 
        print(f'The nickname of this client is: {name}'.encode('utf-8'))
        #print(broadcast(f'{name} has entered the chat.'.encode('utf-8'), name))
        broadcast(f'{name} has entered the chat.'.encode('utf-8'), name) 
        #print(client.send('You have connected!'.encode('utf-8')))
        #client.send(encrypt('You have connected!'.encode('utf-8'), 3))

        # start new thread to handle each clients messages 
        thread = threading.Thread(target = handle_client, args =(client,))
        thread.start()

if __name__ == "__main__":
    receive()
