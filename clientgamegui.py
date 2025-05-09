import tkinter as tk
from tkinter import scrolledtext
import random

import tkinter as tk
from tkinter import scrolledtext
import threading
import random
import socket
# GUI For the game screen 
class ClientGameGUI:
    def __init__(self, root, client_socket):
        self.client_socket = client_socket

        self.chatWindow3 = tk.Toplevel(root)
        self.chatWindow3.geometry("550x520")
        self.chatWindow3.title("Game")

        # Load random battle background
        self.background = tk.PhotoImage(file=f"battle{random.randint(1, 5)}.png")

        self.setup_layout()
        self.start_game_socket_thread()  # <--- Start listening to the server

    def setup_layout(self):
        self.top_left_frame = tk.Frame(self.chatWindow3, width=275, height=260, bg="white")
        self.top_left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.top_right_frame = tk.Frame(self.chatWindow3, width=275, height=260, bg="lightgray")
        self.top_right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.bottom_left_frame = tk.Frame(self.chatWindow3, width=275, height=260, bg="white")
        self.bottom_left_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.bottom_right_frame = tk.Frame(self.chatWindow3, width=275, height=260, bg="lightgray")
        self.bottom_right_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        self.chatWindow3.grid_rowconfigure(0, weight=1)
        self.chatWindow3.grid_rowconfigure(1, weight=1)
        self.chatWindow3.grid_columnconfigure(0, weight=200)
        self.chatWindow3.grid_columnconfigure(1, weight=1)

        self.pokemon_label = tk.Label(self.top_left_frame, image=self.background, bg="white")
        self.pokemon_label.pack(expand=True, fill="both")

        self.game_log = scrolledtext.ScrolledText(self.top_right_frame, wrap=tk.WORD, state=tk.DISABLED, width=30)
        self.game_log.pack(expand=True, fill="both", padx=5, pady=5)

        self.hp_labels = []
        for i in range(3):
            hp_frame = tk.Frame(self.bottom_left_frame, bg="white", height=80, width=275)
            hp_frame.pack(fill="x", expand=True, padx=5, pady=5)
            hp_label = tk.Label(hp_frame, text=f"Pokemon {i+1}: HP 100/100", font=("Arial", 12), bg="white")
            hp_label.pack(expand=True, fill="both")
            self.hp_labels.append(hp_label)

        command_label = tk.Label(self.bottom_right_frame, text="Enter Command:", font=("Arial", 10), bg="lightgray")
        command_label.pack(anchor="w", padx=5, pady=5)

        self.command_input = tk.Entry(self.bottom_right_frame, width=40)
        self.command_input.pack(padx=5, pady=5)
        self.command_input.bind("<Return>", self.send_command_to_server)

    def start_game_socket_thread(self):
        thread = threading.Thread(target=self.receive_message_from_server, daemon=True)
        thread.start()

    def receive_message_from_server(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if not message:
                    break
                self.display_game_message(message)
            except Exception as e:
                self.display_game_message(f"Error receiving: {e}")
                break

    def send_command_to_server(self, event=None):
        message = self.command_input.get().strip()
        if message:
            try:
                self.client_socket.send(message.encode())
            except Exception as e:
                self.display_game_message(f"Failed to send: {e}")
            self.command_input.delete(0, tk.END)

    def display_game_message(self, message):
        self.game_log.config(state=tk.NORMAL)
        self.game_log.insert(tk.END, message + "\n")
        self.game_log.config(state=tk.DISABLED)
        self.game_log.see(tk.END)
