import tkinter as tk
from tkinter import scrolledtext

class ClientGameGUI:
    def __init__(self, root):
        self.chatWindow3 = tk.Toplevel(root)
        self.chatWindow3.geometry("550x520")
        self.chatWindow3.title("Game")
        self.setup_layout()

    def setup_layout(self):
        # Create frames
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

        # Top Left: Pokémon Image
        self.pokemon_image = tk.PhotoImage(file="pikachu2.png")
        self.pokemon_label = tk.Label(self.top_left_frame, image=self.pokemon_image, bg="white")
        self.pokemon_label.pack(expand=True, fill="both")

        # Top Right: Game Log
        self.game_log = scrolledtext.ScrolledText(self.top_right_frame, wrap=tk.WORD, state=tk.DISABLED, width=30)
        self.game_log.pack(expand=True, fill="both", padx=5, pady=5)

        # Bottom Left: Pokémon HP display
        self.hp_labels = []
        for i in range(3):
            hp_frame = tk.Frame(self.bottom_left_frame, bg="white", height=80, width=275)
            hp_frame.pack(fill="x", expand=True, padx=5, pady=5)
            hp_label = tk.Label(hp_frame, text=f"Pokemon {i+1}: HP 100/100", font=("Arial", 12), bg="white")
            hp_label.pack(expand=True, fill="both")
            self.hp_labels.append(hp_label)

        # Bottom Right: Command Input
        command_label = tk.Label(self.bottom_right_frame, text="Enter Command:", font=("Arial", 10), bg="lightgray")
        command_label.pack(anchor="w", padx=5, pady=5)

        self.command_input = tk.Entry(self.bottom_right_frame, width=40)
        self.command_input.pack(padx=5, pady=5)
        self.command_input.bind("<Return>", self.handle_command)

        self.pokemon_label.image = self.pokemon_image

    def handle_command(self, event=None):
        command = self.command_input.get().strip()
        if command:
            self.game_log.config(state=tk.NORMAL)
            self.game_log.insert(tk.END, f"You: {command}\n")
            self.game_log.config(state=tk.DISABLED)
            self.game_log.see(tk.END)
            self.command_input.delete(0, tk.END)

    def display_game_message(self, message):
        self.game_log.config(state=tk.NORMAL)
        self.game_log.insert(tk.END, message + "\n")
        self.game_log.config(state=tk.DISABLED)
        self.game_log.see(tk.END)

