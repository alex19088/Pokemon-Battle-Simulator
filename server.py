import socket
import threading
import time 
import PokemonObjects5
import alexPokemon
# Test # Test 2
class Server:
    def __init__(self, host='localhost', port=65000, clients=[], nicknames=[], hours=0, minutes=0, seconds=0, done=False):
        self.host = host
        self.port = port
        self.clients = clients # The list of clients 
        self.nicknames = nicknames # Nickname for each client (for chat)
        self.hours = hours # For time display
        self.minutes = minutes # For time display
        self.seconds= seconds # For time display
        self.done = done # To stop the server (for while loops)
        self.clients_lock = threading.Lock()
    
    # Purpose: To update the live chat time
    def time_update(self):
        while not self.done:
            time.sleep(1)
            self.seconds += 1 

            if self.seconds == 60:
                self.seconds = 0
                self.minutes += 1
            if self.minutes == 60:
                self.minutes = 0
                self.hours += 1
                
    # Purpose: To broadcast a message to all clients
    def broadcast(self, message):
        time_display = f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}"
        for client in self.clients:
            client.send(f"[{time_display}] {message}".encode())

    # Purpose: To constantly receive and broadcast messages to clients via TCP
    def handle_client(self, client):
        while not self.done:
            try:
                message = client.recv(1024).decode()
                self.broadcast(message)
            except:
                # Removing the client from the list of clients
                index = self.clients.index(client)
                self.clients.remove(client)
                
                client.close() # Closing the connection for that client

                # Removing the clients nickname from the list of nicknames
                nickname = self.nicknames[index]
                self.broadcast(f"[{nickname}] disconnected from the chat!".encode())
                self.nicknames.remove(nickname)
                break
        

    # Purpose: To start the chatroom 
    def start_chatroom(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Initializing server socket

        server.bind((self.host, self.port)) # Binding the server to localhoost and a valid port number 

        server.listen(3) # Listening for 3 players 

        # Live timer
        timer = threading.Thread(target=self.time_update)
        timer.start()

        # Constantly accepting client connections
        while not self.done:
            client, addr = server.accept()

            client.send("NICK".encode()) # To notify clients to enter a nickname when joining the chat

            nickname = client.recv(1024).decode() # Extracting the nickname the client sent 
            self.nicknames.append(nickname) # Appending the nickname to the list of nicknames
            # Making it so only one thread can add clients to the list at a time (prevent duplicate clients)
            with self.clients_lock:
                if client not in self.clients:
                    self.clients.append(client) # Appending the client socket to the list of clients

            print(f"Nickname of the client is {nickname}")
            
            client.send("Welcome to the Chatroom! Please refrain from any toxicity.\n".encode()) # Notifying the client that they connected to the server

            self.broadcast(f"{nickname} joined the chat!") # Notifying other clients that a new client joined the chat
            

            handler = threading.Thread(target=self.handle_client, args=(client,)) 
            handler.start() # Starting the client handler
    
    def start_game_loop(self):
        while not self.done:
            with self.clients_lock:
                pass # wip


if __name__ == "__main__":
    server = Server()
    chat = threading.Thread(target=server.start_chatroom)
    chat.start()

    


