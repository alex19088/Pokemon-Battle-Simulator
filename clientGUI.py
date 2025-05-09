import socket
import threading
import tkinter as tk
from tkinter import scrolledtext


from clientgamegui import ClientGameGUI


class ClientClass:
    def __init__(self, host='localhost', port=65000):
        self.host = host
        self.port = port
        self.client = None
        self.nickname = ""
      
    # Purpose: To receieve tcp messages from the server
    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode() # If the message is NICK, send the server the clients chosen nickname
                if message == "NICK":
                    self.client.send(self.nickname.encode())
                elif message.startswith("Available Pokemon:") or "Confirm?" in message or "added to your team!" in message:
                    client_game_gui.display_game_message(message) # If the message starts with these phrases, output the message in the game window
                else:
                    if ": " in message: # If the message contains ":", its a chatroom message
                        sender, msg = message.split(": ", 1)
                        

                        chatwindowDisplay.config(state=tk.NORMAL)
                        chatwindowDisplay.tag_config(sender, font=("Arial", 10, "bold"))
                        chatwindowDisplay.insert(tk.END, f"{sender}: ", sender)
                        chatwindowDisplay.insert(tk.END, f"{msg}\n")
                        chatwindowDisplay.config(state=tk.DISABLED)
                        chatwindowDisplay.see(tk.END)
                    else:
                        chatwindowDisplay.config(state=tk.NORMAL)
                        chatwindowDisplay.insert(tk.END, message + "\n")  # <
                        chatwindowDisplay.config(state=tk.DISABLED)
                        chatwindowDisplay.see(tk.END)
            except Exception as e:
                print("Error receiving:", e)
                self.client.close()
                break
    # Purpose: Allow client to type a message and send it to the server
    def write_message(self, event=None):
        user_input = inputChat.get().strip()
        if user_input:
            message = f"{self.nickname}: {user_input}"
            try:
                self.client.send(message.encode())
               
            except:
                print("Error sending message")
            inputChat.delete(0, tk.END)

    # Purpose: To connect to the server and constantly receive messages
    def start(self, nickname):
        self.nickname = nickname
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))

        recv_thread = threading.Thread(target=self.receive, daemon=True)
        recv_thread.start()

# For the game loop
class ClientGame:
    def __init__(self, host='localhost', port=65000):
        self.host = host
        self.port = port
        self.client = None
        self.nickname = ""

    # Purpose: start the game connection
    def start_game(self, nickname):
        self.nickname = nickname
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))

        # Start receiving messages from the server in a separate thread
        recv_thread = threading.Thread(target=self.receive_game, daemon=True)
        recv_thread.start()


# purpose: Let each user pick a nickname and then config the label to accurately update 
# Let user pick a nickname and create the game window
def handle_nickname(event):
    nickname = inputChat.get().strip()
    if nickname:
        inputChat.delete(0, tk.END)
        label1.config(text="Type and press Enter to chat!")
        inputChat.unbind("<Return>")
        inputChat.bind("<Return>", clientclass.write_message)
        clientclass.start(nickname)

        # Pass the existing socket from ClientClass into the game GUI
        global client_game_gui
        client_game_gui = ClientGameGUI(chatWindow, clientclass.client)



# GUI Setup for chat room
chatWindow = tk.Tk()
chatWindow.geometry("350x520")
chatWindow.title("Chat Room")

photoICON = tk.PhotoImage(file='chatICON.png')
chatWindow.iconphoto(False, photoICON)

chatwindowDisplay = scrolledtext.ScrolledText(chatWindow, wrap=tk.WORD, width=50, height=20, state=tk.DISABLED)
chatwindowDisplay.pack(padx=10, pady=10)

label1 = tk.Label(chatWindow, text="Enter your nickname and press Enter:", font=('Arial', 10))
label1.pack()

inputChat = tk.Entry(chatWindow, width=50)
inputChat.pack(padx=10, pady=10)

photo1 = tk.PhotoImage(file='pikachu2.png')
label2 = tk.Label(chatWindow, image=photo1)
label2.pack()

clientclass = ClientClass()
inputChat.bind("<Return>", handle_nickname)

chatWindow.mainloop()
