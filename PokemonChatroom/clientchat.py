import socket
import threading

class ClientChatroom:
    def __init__(self, host='localhost', port=65000, done=False):
        self.host = host
        self.port = port
        self.done = done

    # Purpose: To recieve messages from the server
    def receive(self, client):
        while not self.done:
            try:
                message = client.recv(1024).decode() # Receiving messages
                if message == "NICK": 
                    client.send(nickname.encode()) # Send the clients chosen nickname to the server
                else:
                    print(message) 
            except: 
                print("An error occured")
                client.close()
                break

    # Purpose: To send messages to the server
    def write_message(self, client):
        while not self.done:
            message = f"{nickname}: {input("")}"
            client.send(message.encode())
    
    # Purpose: To start the client connection to the server
    def start(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.host, self.port))

        recv_thread = threading.Thread(target=self.receive, args=(client,))
        recv_thread.start()

        write_thread = threading.Thread(target=self.write_message, args=(client,))
        write_thread.start()

if __name__ == "__main__":
    nickname = input("Choose a nickname: ")
    chat = ClientChatroom()
    chat.start()