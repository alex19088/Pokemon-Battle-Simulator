import socket
import threading
import os
import tkinter as tk #
from tkinter import scrolledtext #

window = tk.Tk()
window.geometry("350x520")
window.title("Chat Room")
photoICON = tk.PhotoImage(file='chatICON.png')
window.iconphoto(False, photoICON)

class ClientChatroom:
    def __init__(self, host='localhost', port=65000, done=False):
        self.host = host
        self.port = port
        self.done = done
        self.nickname_colors = {}  # Dictionary to store nickname-color mapping

    # assign unique color to trainer
    def assign_color(self, nickname):
        colors = ["green", "blue", "red"]  # Add more colors if needed
        if nickname not in self.nickname_colors:
            self.nickname_colors[nickname] = colors[len(self.nickname_colors) % len(colors)]
        return self.nickname_colors[nickname]

    # Purpose: To recieve messages from the server
    def receive(self, client):
        while not self.done:
            try:
                message = client.recv(1024).decode() # Receiving messages
                if message == "NICK": 
                    client.send(nickname.encode()) # Send the clients chosen nickname to the server
                else:
                    # Extract nickname and message
                    sender, msg = message.split(": ", 1)
                    color = self.assign_color(sender)

                    # Display the message with the sender's color
                    chat_display.config(state=tk.NORMAL)
                    chat_display.tag_config(sender, foreground=color, font=("Arial", 10, "bold"))
                    chat_display.insert(tk.END, f"{sender}: ", sender)
                    chat_display.insert(tk.END, f"{msg}\n")
                    chat_display.config(state=tk.DISABLED)
                    chat_display.see(tk.END)
            except: 
                print("An error occured")
                client.close()
                break

    # Purpose: To send messages to the server
    def write_message(self, client):
        user_input = input_field.get().strip()  # Get user input and remove extra spaces

        if user_input:  # Only proceed if the input is not empty
            # Send the message to the server
            message = f"{nickname}: {user_input}"
            client.send(message.encode())

            # Display the users message in their color
            chat_display.config(state=tk.NORMAL)
            color = self.assign_color(nickname)
            chat_display.tag_config(nickname, foreground=color, font=("Arial", 10, "bold"))
            chat_display.insert(tk.END, f"You: ", nickname)
            chat_display.insert(tk.END, f"{user_input}\n")
            chat_display.config(state=tk.DISABLED)
            chat_display.see(tk.END)

            # Clear the input field
            input_field.delete(0, tk.END)

    # Purpose: To start the client connection to the server
    def start(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.host, self.port))

        recv_thread = threading.Thread(target=self.receive, args=(client,))
        recv_thread.start()

        write_thread = threading.Thread(target=self.write_message, args=(client,))
        write_thread.start()

def handle_nickname(event):
    global nickname
    nickname = input_field.get()
    input_field.delete(0, tk.END)
    label.config(text="Type and press 'Enter' to chat!")
    input_field.bind("<Return>", lambda event: ClientChatroom.send_message())

if __name__ == "__main__":

    chat_display = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=50, height=20, state=tk.DISABLED)
    chat_display.pack(padx=10, pady=10)

    label = tk.Label(window, text="Type and press 'Enter' to chat!", font=('Arial', 10), fg='Black')
    label.pack()

    input_field = tk.Entry(window, width= 50)
    input_field.pack(padx=(10,0), pady=(10,0))
    input_field.bind("<Return>", handle_nickname)

    label2 = tk.Label(window, image= tk.PhotoImage(file='pikachu2.png'))
    label2.pack()


    chat = ClientChatroom()
    chat.start()