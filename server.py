import socket
import threading
import time 
import PokemonObjects5
import alexPokemon

# Wrapper class for client objects 
class ClientWrapper:
    def __init__(self, client, nickname):
        self.client = client # The socket object
        self.nickname = nickname # The nickname of the client
        self.trainer_pokemon = [] # The list of pokemons chosen by the trainer (later on)
        self.active_pokemon = None # The active pokemon of the trainer (later on)
        

class Server:
    def __init__(self, host='localhost', port=65000, clients=[], nicknames=[], hours=0, minutes=0, seconds=0, done=False):
        self.host = host #Change to local ip
        self.port = port
        self.clients = clients # The list of clients 
        self.nicknames = nicknames # Nickname for each client (for chat)
        self.hours = hours # For time display
        self.minutes = minutes # For time display
        self.seconds= seconds # For time display
        self.done = done # To stop the server (for while loops)
        self.trainers = []
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
    # Purpose: Broadcast the message to all clients 
    def broadcast(self, message):
        time_display = f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}"
        for client_obj in self.clients:
            try:
                client_obj.client.send(f"[{time_display}] {message}".encode())
            except:
                pass  


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
                self.broadcast(f"[{nickname}] disconnected from the chat!")
                self.nicknames.remove(nickname)
                break


    
    # Purpose: To let the trainer choose a pokemon
    def choose_pokemon(self, client_obj):
        client = client_obj.client
        # Display available pokemon to client
        while True:
            message = "Available Pokemon:\n"
            available = []
            for idx, poke in enumerate(all_pokemon):
                if not poke.is_chosen:
                    available.append((idx + 1, poke))
                    message += f"{idx + 1}: {poke.name}\n"
            message += "Choose a Pokemon by number:\n"
            client.sendall(message.encode())
            # Receive pokemon choice from client, checking if its a valid input also
            try:
                response = client.recv(1024).decode().strip()      
                choice = int(response)
            except:
                client.sendall("Error receiving input.\n".encode())
                continue
            
            if choice < 1 or choice > len(all_pokemon):
                client.sendall("Choice out of range.\n".encode())
                continue

            chosen_pokemon = all_pokemon[choice - 1]
            if chosen_pokemon.is_chosen:
                client.sendall("This Pokemon is already taken.\n".encode())
                continue
            # Ask for confirmation and display pokemon selected
            client.sendall(f"{chosen_pokemon.name}".encode())
            client.sendall(f"\nConfirm? (1: Yes, 2: No):\n".encode())
            confirm = client.recv(1024).decode().strip().lower()
            # If chosen, append the pokemon to the clients pokemon team
            if confirm in ["1", "yes"]:
                chosen_pokemon.is_chosen = True
                client_obj.trainer_pokemon.append(chosen_pokemon)
                client.sendall(f"{chosen_pokemon.name} added to your team!\n".encode())
                return
            elif confirm in ["2", "no"]:
                continue
            else:
                client.sendall("Invalid option. Try again.\n".encode())


    # Purpose: To start the game server
    def start_game(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(3)


        timer = threading.Thread(target=self.time_update, daemon=True)
        timer.start()
        # Only start game once all clients connect
        while len(self.clients) < 3:
            client, addr = server.accept()
            client.send("NICK".encode()) #Notify clients to receieve their nickname
            nickname = client.recv(1024).decode().strip()

            client_obj = ClientWrapper(client, nickname) # Client object for accessing client info (socket, nickname, etc)

            print(f"Nickname of the client is {nickname}")
            with self.clients_lock:
                self.clients.append(client_obj)

            self.nicknames.append(nickname) # Adding the clients nickname to the servers list of nicknames
            self.broadcast(f"{nickname} joined the game!")
            client.send(f"Welcome to alexPokemon!\nWaiting for {3 - len(self.clients)} more player(s).\n".encode())
            client.send("Please refrain from any toxicity.\n".encode())

            handler = threading.Thread(target=self.handle_client, args=(client,)) # Starting the thread for TCP communication
            handler.start()

        self.broadcast("All players connected! Starting game...")

        for i in range(3):  # 3 rounds of choosing
            for client_obj in self.clients:
                self.choose_pokemon(client_obj)
                self.broadcast(f"{client_obj.nickname} chose a Pokemon!") 


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
    game.join()

    


