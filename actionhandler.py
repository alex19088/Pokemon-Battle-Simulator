from abc import ABC, abstractmethod


# Class for sending the actions to clients via TCP
class ActionHandler:
    # Purpose: To tell the client to pick a pokemon (start of the game)
    def pick(self, client):
        client.sendall(f"PICK".encode())
    
    # Purpose: To notify the clients that its their turn 
    def notify(self, client):
        client.sendall("NOTIFY".encode())

# Abstract class
class Action(ABC):
    @abstractmethod
    def execute(self):
        pass

# Concrete action Classes
class PickAction(Action):
    def __init__(self, action : ActionHandler, client):
        self.action = action
        self.client = client
      
    
    def execute(self):
        self.action.pick(self.client)

class NotifyAction(Action):
    def __init__(self, action : ActionHandler, client):
        self.action = action
        self.client = client
    
    def execute(self):
        self.action.notify(self.client)

