from typing import List, Tuple
from abc import ABC, abstractmethod
import random
import json
import tkinter as tk
from tkinter import scrolledtext

# Purpose: load predefined Q&A pairs from JSON and log unrecognized queries
class Query_Database:
    def __init__(self, filepath: str = "queries.json"):
        with open(filepath, "r", encoding='utf-8') as f:
            self.queries = json.load(f)

    def writeUnrecognized(self, user_input: str) -> None:
        with open("unrecognized_queries.txt", "a", encoding='utf-8') as log:
            log.write(user_input + "\n")

    def lookup_response(self, section: str, user_input: str) -> str:
        text = user_input.lower().strip()
        for entry in self.queries.get(section, []):
            q = entry.get("Question", "").lower().strip()
            if q and q in text:
                answers = entry.get("Answer", [])
                if answers:
                    return random.choice(answers)
        self.writeUnrecognized(user_input)
        return None

# Observer for sentiment escalation
class Observer(ABC):
    @abstractmethod
    def update(self, user_input: str, session: dict) -> str:
        pass

class SentimentObserver(Observer):
    negative_words = ["angry", "frustrated", "hate", "worst", "stupid", "this sucks"]

    def update(self, user_input: str, session: dict) -> str:
        if any(w in user_input.lower() for w in self.negative_words):
            session['escalate'] = True
            return "I sense frustration—I'll connect you with support if needed."
        return None

# Stubbed backend manager (unused for static responses)
class backendManager:
    def process_request(self) -> str:
        return ""

# Base handler interface
class IQueryHandler(ABC):
    @abstractmethod
    def handle_query(self, user_input: str, session: dict, qdb: Query_Database, backend: backendManager) -> str:
        pass

# Handler for attack-related questions
class AttackInfoHandler(IQueryHandler):
    def handle_query(self, user_input, session, qdb, backend) -> str:
        resp = qdb.lookup_response("attack_info", user_input)
        return resp or "Ask me about physical vs. special attacks or how critical hits work."

# Handler for type-effectiveness questions
class TypeInfoHandler(IQueryHandler):
    def handle_query(self, user_input, session, qdb, backend) -> str:
        resp = qdb.lookup_response("type_info", user_input)
        return resp or "I can explain type strengths and weaknesses—try asking 'what is fire strong against?'."

# Handler for item-related questions
class ItemInfoHandler(IQueryHandler):
    def handle_query(self, user_input, session, qdb, backend) -> str:
        resp = qdb.lookup_response("item_info", user_input)
        return resp or "Need details on Potions, Berries, or other items? Just ask!"

# Handler for game mechanics questions
class MechanicHandler(IQueryHandler):
    def handle_query(self, user_input, session, qdb, backend) -> str:
        resp = qdb.lookup_response("mechanics", user_input)
        return resp or "I can cover mechanics like turn order, status effects, and catching Pokemon."

# General/fallback handler
class GeneralHandler(IQueryHandler):
    def handle_query(self, user_input, session, qdb, backend) -> str:
        resp = qdb.lookup_response("general", user_input)
        return resp or "I'm your Pokemon battle support—ask me anything about attacks, types, items, or mechanics."

class DefaultHandler(IQueryHandler):
    def handle_query(self, user_input, session, qdb, backend) -> str:
        qdb.writeUnrecognized(user_input)
        return "Sorry, I didn't understand that. Could you rephrase?"

# Factory for mapping intents to handlers
class QueryManager:
    handlers = {
        "attack": AttackInfoHandler,
        "type": TypeInfoHandler,
        "item": ItemInfoHandler,
        "mechanics": MechanicHandler,
        "general": GeneralHandler
    }
    @staticmethod
    def get_handler(intent: str) -> IQueryHandler:
        return QueryManager.handlers.get(intent, DefaultHandler)()

# Core chatbot class
class Chatbot:
    def __init__(self, qdb, recognizer, backend, factory):
        self.sessions = {}
        self.qdb = qdb
        self.recognizer = recognizer
        self.backend = backend
        self.factory = factory
        self.observers = [SentimentObserver()]

    def notify_observers(self, text: str, session: dict) -> str:
        for obs in self.observers:
            res = obs.update(text, session)
            if res:
                return res
        return None

    def process_input(self, user_input: str, user_id: str) -> str:
        session = self.sessions.setdefault(user_id, {})
        esc = self.notify_observers(user_input, session)
        if esc:
            return esc
        intent = self.recognizer.recognize_intent(user_input)
        handler = self.factory.get_handler(intent)
        resp = handler.handle_query(user_input, session, self.qdb, self.backend)
        return resp

# Intent recognizer based on synonyms and JSON entries
class intentRecognizer:
    def __init__(self, qdb):
        self.qdb = qdb
        self.synonyms = {
            "attack": ["special attack", "physical attack", "critical hit", "move power", "stab"],
            "type": ["strong against", "weak to", "super effective", "not very effective", "immunity"],
            "item": ["potion", "berry", "use item", "heal hp"],
            "mechanics": ["turn order", "status effect", "catch chance", "experience gain"],
            "general": ["hello", "hi", "help", "info", "support"]
        }

    def recognize_intent(self, user_input: str) -> str:
        txt = user_input.lower()
        for intent, words in self.synonyms.items():
            if any(w in txt for w in words):
                return intent
        for section, entries in self.qdb.queries.items():
            for entry in entries:
                if entry.get("Question", "").lower() in txt:
                    return section
        return "unrecognized"

# UI setup
window = tk.Tk()
window.geometry("350x520")
window.title("AI Assistance")
photo1 = tk.PhotoImage(file='pikachu.png')

def send_message():
    msg = input_field.get().strip()
    chat_display.tag_config("user_tag", foreground="green", font=("Arial",10,"bold"))
    chat_display.tag_config("bot_tag", foreground="blue", font=("Arial",10,"bold"))
    if not msg:
        return
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, f"You: {msg}\n")
    chat_display.config(state=tk.DISABLED)
    chat_display.see(tk.END)

    response = bot.process_input(msg, "player")

    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, f"Chatbot: {response}\n")
    chat_display.config(state=tk.DISABLED)
    chat_display.see(tk.END)
    input_field.delete(0, tk.END)

if __name__ == "__main__":
    chat_display = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=50, height=20, state=tk.DISABLED)
    chat_display.pack(padx=10, pady=10)

    label = tk.Label(window, text="Type and press 'Enter' to talk", font=('Arial',10))
    label.pack()

    input_field = tk.Entry(window, width=50)
    input_field.pack(padx=10, pady=(0,10))
    input_field.bind("<Return>", lambda e: send_message())

    label2 = tk.Label(window, image=photo1)
    label2.pack()

    query_db = Query_Database()
    intent_recognizer = intentRecognizer(query_db)
    backend_manager = backendManager()
    handler_factory = QueryManager
    bot = Chatbot(query_db, intent_recognizer, backend_manager, handler_factory)

    window.mainloop()
