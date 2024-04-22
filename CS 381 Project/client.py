import threading 
import socket 

#get clients nickname for chatroom 
name = input('Choose a nickname: ')

#connect to server 
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 59000))

# encrypt and decrypt function follows same logic as the server functions 
def encrypt(message, key):
    encrypted_message = ""
    for char in message:
        if char.isalpha():
            shifted = ord(char) + key
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
            encrypted_message += char
    #print(encrypted_message, "encrypted")
    return encrypted_message

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
            decrypted_message += char
    #print(decrypted_message, "decrypted")
    return decrypted_message

#receive messages from server 
def client_receive():
    while True: 
        try: 
            #receive adn decrypt messages from the server 
            encrypted_message = client.recv(1024).decode('utf-8')

            #send client name if requested and print the received messages 
            if encrypted_message == "name?":
                client.send(name.encode('utf-8'))
            else: 
                decrypted_message = decrypt(encrypted_message, 3)
                #print("Received encrypted message:", encrypted_message)
                #print("Decrypted message before printing:", decrypted_message)
                print(decrypted_message)
        except: 
            #testing
            print('Error!')
            client.close()
            break 

#send messages to server 
def client_send(): 
    while True: 
        message = f'{name}: {input("")}' # receive messages 
        encrypted_message = encrypt(message, 3) # ecnrypt 
        try:
            client.send(encrypted_message.encode('utf-8')) # send encrypted messages to sserver
        except ConnectionError:
            #pls do not break the server !!
            print('Connection with the server has been lost.')
            break

#thread to receive messages from the server 
receive_thread = threading.Thread(target=client_receive)
receive_thread.start()

#thread 4 sending messages to the server 
send_thread = threading.Thread(target = client_send)
send_thread.start()

# >-<
