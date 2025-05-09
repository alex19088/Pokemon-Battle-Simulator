import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

class ClientChatroom:
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
                else:
                   
                    if ": " in message:
                        sender, msg = message.split(": ", 1)
                        color = self.assign_color(sender)

                        chat_display.config(state=tk.NORMAL)
                        chat_display.tag_config(sender, foreground=color, font=("Arial", 10, "bold"))
                        chat_display.insert(tk.END, f"{sender}: ", sender)
                        chat_display.insert(tk.END, f"{msg}\n")
                        chat_display.config(state=tk.DISABLED)
                        chat_display.see(tk.END)
                    else:
                        # System message
                        chat_display.config(state=tk.NORMAL)
                        chat_display.insert(tk.END, message + "\n")
                        chat_display.config(state=tk.DISABLED)
                        chat_display.see(tk.END)

            except Exception as e:
                print("Error receiving:", e)
                self.client.close()
                break

    def write_message(self, event=None):
        user_input = input_field.get().strip()
        if user_input:
            message = f"{self.nickname}: {user_input}"
            try:
                self.client.send(message.encode())  # Send the message to the server
            except:
                print("Error sending message")
            # Clear the input field (but do not display the message locally)
            input_field.delete(0, tk.END)

    def start(self, nickname):
        self.nickname = nickname
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))

        recv_thread = threading.Thread(target=self.receive, daemon=True)
        recv_thread.start()

# GUI Setup 
window = tk.Tk()
window.geometry("350x520")
window.title("Chat Room")


photoICON = tk.PhotoImage(file='chatICON.png')
window.iconphoto(False, photoICON)


chat_display = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=50, height=20, state=tk.DISABLED)
chat_display.pack(padx=10, pady=10)

label = tk.Label(window, text="Enter your nickname and press Enter:", font=('Arial', 10))
label.pack()

input_field = tk.Entry(window, width=50)
input_field.pack(padx=10, pady=10)

photo = tk.PhotoImage(file='pikachu2.png')
label2 = tk.Label(window, image=photo)
label2.pack()

chat = ClientChatroom()

def handle_nickname(event):
    nickname = input_field.get().strip()
    if nickname:
        input_field.delete(0, tk.END)
        label.config(text="Type and press Enter to chat!")
        input_field.unbind("<Return>")
        input_field.bind("<Return>", chat.write_message)
        chat.start(nickname)

input_field.bind("<Return>", handle_nickname)

window.mainloop()
