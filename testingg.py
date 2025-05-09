import tkinter as tk
from tkinter import scrolledtext



# --- GUI setup for game interface ---
chatWindow3 = tk.Toplevel(chatWindow)  # Create new window
chatWindow3.geometry("550x520")  # Keep the specified dimensions
chatWindow3.title("Game Room")

# Create frames for each section
top_left_frame = tk.Frame(chatWindow3, width=275, height=260, bg="white")
top_left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

top_right_frame = tk.Frame(chatWindow3, width=275, height=260, bg="lightgray")
top_right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

bottom_left_frame = tk.Frame(chatWindow3, width=275, height=260, bg="white")
bottom_left_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

bottom_right_frame = tk.Frame(chatWindow3, width=275, height=260, bg="lightgray")
bottom_right_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

# Configure grid weights for resizing
chatWindow3.grid_rowconfigure(0, weight=1)
chatWindow3.grid_rowconfigure(1, weight=1)
chatWindow3.grid_columnconfigure(0, weight=200)  # Left column (image and HP sections, 5/6 of the width)
chatWindow3.grid_columnconfigure(1, weight=1)  # Right column (scrolling text widget, 1/6 of the width)

# Top Left: Pokémon fight image
pokemon_image = tk.PhotoImage(file="pikachu2.png")  # Replace with your image path
pokemon_label = tk.Label(top_left_frame, image=pokemon_image, bg="white")
pokemon_label.pack(expand=True, fill="both")

# Top Right: Scrolling text widget (game log)
game_log = scrolledtext.ScrolledText(top_right_frame, wrap=tk.WORD, state=tk.DISABLED, width=30)
game_log.pack(expand=True, fill="both", padx=5, pady=5)

# Bottom Left: Pokémon HP display (3 sections)
for i in range(3):
    hp_frame = tk.Frame(bottom_left_frame, bg="white", height=80, width=275)
    hp_frame.pack(fill="x", expand=True, padx=5, pady=5)
    hp_label = tk.Label(hp_frame, text=f"Pokémon {i+1}: HP 100/100", font=("Arial", 12), bg="white")
    hp_label.pack(expand=True, fill="both")

# Bottom Right: Input box for commands
command_label = tk.Label(bottom_right_frame, text="Enter Command:", font=("Arial", 10), bg="lightgray")
command_label.pack(anchor="w", padx=5, pady=5)

command_input = tk.Entry(bottom_right_frame, width=40)
command_input.pack(padx=5, pady=5)

# Bind Enter key to handle commands
def handle_command(event=None):
    user_command = command_input.get().strip()
    if user_command:
        game_log.config(state=tk.NORMAL)
        game_log.insert(tk.END, f"You: {user_command}\n")
        game_log.config(state=tk.DISABLED)
        game_log.see(tk.END)
        command_input.delete(0, tk.END)

command_input.bind("<Return>", handle_command)

# Keep a reference to the image to prevent garbage collection
pokemon_label.image = pokemon_image

chatWindow3.mainloop()  # Start the main event loop
