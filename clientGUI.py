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
        self.nickname_colors = {}
        self.nickname = ""

    def assign_color(self, nickname):
        colors = ["green", "blue", "red", "purple", "orange"]
        if nickname not in self.nickname_colors:
            self.nickname_colors[nickname] = colors[len(self.nickname_colors) % len(colors)]
        return self.nickname_colors[nickname]

    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode()
                if message == "NICK":
                    self.client.send(self.nickname.encode())
                elif message == "PICK":
                    pass
                elif message.startswith("Available Pokemon:") or "Confirm?" in message or "added to your team!" in message:
                    client_game_gui.display_game_message(message)
                else:
                    if ": " in message:
                        sender, msg = message.split(": ", 1)
                        color = self.assign_color(sender)

                        chatwindowDisplay.config(state=tk.NORMAL)
                        chatwindowDisplay.tag_config(sender, foreground=color, font=("Arial", 10, "bold"))
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

    def write_message(self, event=None):
        user_input = inputChat.get().strip()
        if user_input:
            message = f"{self.nickname}: {user_input}"
            try:
                self.client.send(message.encode())
            except:
                print("Error sending message")
            inputChat.delete(0, tk.END)

    def start(self, nickname):
        self.nickname = nickname
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))

        recv_thread = threading.Thread(target=self.receive, daemon=True)
        recv_thread.start()

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
'''''
    # Purpose: receive game-related messages (e.g. Pokémon selection)
    def receive_game(self):
        while True:
            try:
                message = self.client.recv(1024).decode()
                if message == "NICK":
                    self.client.send(self.nickname.encode())
                elif message.startswith("Available Pokemon:"):
                    client_game_gui.display_game_message("It's your turn to choose a Pokémon!")
                    client_game_gui.display_game_message(message)

                    # Keep printing the rest of the list and the confirm prompt
                    while True:
                        more = self.client.recv(1024).decode()
                        client_game_gui.display_game_message(more)
                        if "Confirm?" in more:
                            break

                    # Prompt in terminal (you can switch this to GUI later if you want)
                    choice = input("Choose a Pokémon by number: ").strip()
                    self.client.send(choice.encode())

                    # Display Pokémon info
                    poke_info = self.client.recv(1024).decode()
                    client_game_gui.display_game_message(poke_info)

                    confirm = input("Confirm this choice? (1: Yes, 2: No): ").strip()
                    self.client.send(confirm.encode())

                else:
                    client_game_gui.display_game_message(message)
            except Exception as e:
                print("Error receiving:", e)
                self.client.close()
                break
'''

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

        global client_game_gui
        client_game_gui = ClientGameGUI(chatWindow) # thread here ?


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
