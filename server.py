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
        

    # To start the game server for clients
    def start_game(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Initializing server socket

        server.bind((self.host, self.port)) # Binding the server to localhost and a valid port number 

        server.listen(3) # Listening for 3 players 

        # Live timer
        
        timer = threading.Thread(target=self.time_update, daemon=True)
        timer.start()

        # Accept connections until 3 players have joined, and starting the chatroom
        while not len(self.clients) == 3:
            client, addr = server.accept()
            client.send("NICK".encode()) # To notify clients to enter a nickname when joining the chat

            nickname = client.recv(1024).decode() # Extracting the nickname the client sent 
            self.nicknames.append(nickname) # Appending the nickname to the list of nicknames

            print(f"Nickname of the client is {nickname}")

            # Making it so only one thread can add clients to the list at a time (prevent duplicate clients)
            with self.clients_lock:
                if client not in self.clients:
                    self.clients.append(client) # Appending the client socket to the list of clients

            self.broadcast(f"{nickname} joined the game!") # Notifying other clients that a new client joined the chat
            client.send(f"Welcome to alexPokemon! Waiting for {3 - len(self.clients)} more player(s)!".encode())
            client.send("Welcome to the Chatroom! Please refrain from any toxicity.\n".encode())
            handler = threading.Thread(target=self.handle_client, args=(client,)) 
            handler.start() # Starting the client handler
        
        self.broadcast("All players connected! Starting game...")

        for i in range(3):
            for client in self.clients:
                
                client.send("CHOOSEPOKEMON".encode())

            

                

            #with self.clients_lock:
                #pass # wip
    def start_battle(self):
        # trainer pokemon choosing
        for i in range(3):
            for client in self.clients:
                print("\nAvailable Pokemon: ")
                for i in range(len(all_pokemon)):
                    if not all_pokemon[i].is_chosen:
                        print(f"{i + 1}: {all_pokemon[i].name}")
                choose_pokemon(trainer, all_pokemon)

        for trainer in listof_trainer:             
            set_initial_active_pokemon(trainer)


if __name__ == "__main__":
    all_pokemon: list[alexPokemon.Pokemon] = [PokemonObjects5.charizard, PokemonObjects5.ampharos, PokemonObjects5.swampert,
                                  PokemonObjects5.metagross, PokemonObjects5.abomasnow, PokemonObjects5.dusknoir,
                                  PokemonObjects5.pangoro, PokemonObjects5.naganadel, PokemonObjects5.gardevoir,
                                  PokemonObjects5.gengar, PokemonObjects5.rayquaza, PokemonObjects5.grimmsnarl,
                                  PokemonObjects5.garchomp, PokemonObjects5.delphox, PokemonObjects5.duskmanenecrozma,
                                  PokemonObjects5.ironbundle, PokemonObjects5.diancie, PokemonObjects5.guzzlord, 
                                  PokemonObjects5.drowsee, PokemonObjects5.kyurem, PokemonObjects5.torracat, 
                                  PokemonObjects5.mudsdale, PokemonObjects5.vikavolt, PokemonObjects5.snorlax  ]
    server = Server()
    game = threading.Thread(target=server.start_game)
    game.start()
    

    


