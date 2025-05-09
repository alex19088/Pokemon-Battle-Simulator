from typing import List, Tuple
from abc import ABC, abstractmethod
import random
import json 
import tkinter as tk
from tkinter import scrolledtext


window = tk.Tk()

# Purpose: to read the json file and return the queries in a dictionary format
class Query_Database:
    def __init__(self, filepath="queries.json"):
        with open(filepath, "r") as file:
            self.queries = json.load(file)

    # Purpose: to write unrecognized queries to a text file for future reference
    # Contract: writeUnrecognized(user_input: str) -> None
    def writeUnrecognized(self, user_input: str) -> None:
        with open("unrecognized_queries.txt", "a") as f:
            f.write(user_input + "\n")

    # Purpose: normalize the input 
    # Contract: lookup_response(section_name: str, user_input: str) -> str
    def lookup_response(self, section_name, user_input) -> str:
        normalized_input = user_input.lower().strip()
        section = self.queries.get(section_name, [])
        for entry in section:
            question = entry.get("Question", "").lower().strip() # strip and lower the question
            if question in normalized_input:  # if the question is in the user input
                possible_answers = entry.get("Answer", []) # return random answer 
                if possible_answers:
                    return random.choice(possible_answers)
        # If no match is found, log the query and return None.
        self.writeUnrecognized(user_input)
        return None

# Purpose: to define the observer pattern for the sentiment analysis
class Observer(ABC):
    @abstractmethod
    def update(self, user_input, session_data):
        pass

endFlag = False # i wanted the program to end after escalation so im defining this here and making it a global variable 

# Purpose: to detect negative sentiment in user input and escalate the conversation if necessary
class SentimentObserver(Observer):
    negative_words = ["angry", "frustrated", "ridiculous", "this sucks", "hate", "worst", "???", "stupid"]

    # Contract: update(user_input: str, session_data: dict) -> str
    def update(self, user_input, session_data) -> str:
        global endFlag
        text = user_input.lower()
        for word in self.negative_words:
            if word in text:
                session_data["escalate"] = True
                endFlag = True  # end program
                return "I'm really sorry to hear that. Let me connect you to a live agent right away."
        return 

#Purpose: to process a request based on its type and data
class backendManager:
    # Purpose: to process requests for order tracking, refunds, and inventory checks
    # contract: process_request(request_type: str, data: str) -> str
    def process_request(self, request_type, data) -> str:
        if request_type == "order":
            return self.track_order(data)
        elif request_type == "refund":
            return self.process_refund(data)
        elif request_type == "inventory":
            return self.check_inventory(data)
        else:
            return "Service not available."

    # Purpose: to track an order and return a delivery estimate
    # contract: track_order(order_id: str) -> str
    def track_order(self, order_id) -> str:
        # For simulation, randomly choose a delivery estimate in days.
        estimated_days = random.choice([1, 2, 3, 4, 5])
        return f"Your order {order_id} is out for delivery and will arrive in {estimated_days} day(s)."

    # Purpose: to process a refund request and return a confirmation message
    # contract: process_refund(order_id: str, reason: str) -> str
    def process_refund(self, order_id, reason) -> str:
        # Simulate processing the refund with the provided reason
        return (
            f"Your refund request for order {order_id} has been submitted. "
            f"Reason: {reason}. Expect the refund in 5-7 business days."
        )

    # Purpose: to check the inventory for a specific product and return its availability
    # contract: check_inventory(product_name: str) -> str
    def check_inventory(self, product_name) -> str:
        # for simulation, randomly decide if a product is in stock.
        available = random.choice([True, False])
        if available:
            return f"The product '{product_name}' is currently in stock."
        else:
            return f"Unfortunately, the product '{product_name}' is out of stock right now."


# interface or base class (strategy/behavioral)    
class IQueryHandler(ABC):
    @abstractmethod
    def handle_query(self, user_input, session_data, query_database, backend_manager):
        pass

# Purpose: to handle order-related queries and track orders
class OrderHandler(IQueryHandler):
    # Contract: handle_query(user_input: str, session_data: dict, query_database: Query_Database, backend_manager: backendManager) -> str
    def handle_query(self, user_input, session_data, query_database, backend_manager) -> str:
        if session_data.get("awaiting_order_id"):
            # Interpret current input as order ID.
            order_id = user_input.strip()
            session_data["order_id"] = order_id
            session_data["awaiting_order_id"] = False  # Clear the flag.
            return backend_manager.process_request("order", order_id)
        
        response = query_database.lookup_response("orders", user_input)
        if response:
            if "order id" in response.lower():
                session_data["awaiting_order_id"] = True
            return response
        
        session_data["awaiting_order_id"] = True
        return "Please provide your order ID."

# Purpose: to handle refund-related queries and process refunds
class RefundHandler(IQueryHandler):
    # Contract: handle_query(user_input: str, session_data: dict, query_database: Query_Database, backend_manager: backendManager) -> str
    def handle_query(self, user_input, session_data, query_database, backend_manager) -> str:
        # Step 1: If already waiting for refund reason
        if session_data.get("awaiting_refund_reason"):
            reason = user_input.strip()
            session_data["awaiting_refund_reason"] = False
            return backend_manager.process_refund("N/A", reason)

        # Step 2: Check if this is a request for refund(not an inquiry)
        user_lower = user_input.lower()
        if any(phrase in user_lower for phrase in [
            "i want a refund", "i need a refund", "i want to return", "return this", "refund request"
        ]):
            session_data["awaiting_refund_reason"] = True
            return "Sure, I can help with that. Can you tell me the reason for your return?"

        # Step 3: Otherwise its an inquiry so check the database
        response = query_database.lookup_response("refunds", user_input)
        if response:
            return response

        # Step 4: Fallback
        return "Can you clarify your request about refunds?"

# Purpose: to handle inventory-related queries and check product availability
class InventoryHandler(IQueryHandler):
    # Contract: handle_query(user_input: str, session_data: dict, query_database: Query_Database, backend_manager: backendManager) -> str
    def handle_query(self, user_input, session_data, query_database, backend_manager) -> str:
        response = query_database.lookup_response("inventory", user_input)
        if response :
            return response
        return "Please specify the product you're interested in."
    
# Purpose: to handle general queries and provide customer support
class GeneralHandler(IQueryHandler):
    # Contract: handle_query(user_input: str, session_data: dict, query_database: Query_Database, backend_manager: backendManager) -> str
    def handle_query(self, user_input, session_data, query_database, backend_manager):
        response = query_database.lookup_response("general", user_input)
        if response:
            return response
        return "Hello! How can I assist you today?"

# Purpose: to handle payment-related queries and provide payment support
class PaymentHandler(IQueryHandler):
    # Contract: handle_query(user_input: str, session_data: dict, query_database: Query_Database, backend_manager: backendManager) -> str
    def handle_query(self, user_input, session_data, query_database, backend_manager):
        response = query_database.lookup_response("payment", user_input)
        if response:
            return response
        return "There seems to be an issue with your payment. Please check your payment details or try another method."

# Purpose: to handle live agent requests and connect users to a human representative
class AgentHandler(IQueryHandler):
    # Contract: handle_query(user_input: str, session_data: dict, query_database: Query_Database, backend_manager: backendManager) -> str
    def handle_query(self, user_input, session_data, query_database, backend_manager):
        response = query_database.lookup_response("live_agent", user_input)
        if response:
            return response
        return "Connecting you to a live agent now. Please wait a moment."

# Purpose: to handle unrecognized queries and provide a fallback response
class DefaultHandler(IQueryHandler):
    # Contract: handle_query(user_input: str, session_data: dict, query_database: Query_Database, backend_manager: backendManager) -> str
    def handle_query(self, user_input, session_data, query_database, backend_manager):
        query_database.writeUnrecognized(user_input)
        return "I cannot help with that right now and will note this for future updates. Can you can try rephrasing your question?"
    
# My fActory, or creational design pattern
# Purpose: to manage the instantiation of query handlers based on user intent
class QueryManager:
    handlers = {
        "order": OrderHandler,
        "refund": RefundHandler,
        "inventory": InventoryHandler,
        "general": GeneralHandler,
        "payment": PaymentHandler,
        "live_agent": AgentHandler
    }

    # This static factory is used for if the given intent isnt recognized, which will call defualthandler
    @staticmethod
    def get_handler(query_type):
        return QueryManager.handlers.get(query_type, DefaultHandler)()

# Purpose: to manage user sessions and process user input
class Chatbot:
    def __init__(self, query_database, intent_recognizer, backend_manager, handler_factory):
        self.user_sessions = {}
        self.query_database = query_database
        self.intent_recognizer = intent_recognizer
        self.backend_manager = backend_manager
        self.handler_factory = handler_factory
        self.observers = [SentimentObserver()]  # register observer(s)

    def notify_observers(self, user_input, session_data):
        for observer in self.observers:
            result = observer.update(user_input, session_data)
            if result:  # escalation or override message
                return result
        return None

    # Purpose: to process user input and determine the appropriate response
    # Contract: process_input(user_input: str, user_id: str) -> str
    def process_input(self, user_input, user_id):
        session = self.user_sessions.get(user_id, {})

        # Check for emotional escalation
        escalation_response = self.notify_observers(user_input, session)
        if escalation_response:
            self.user_sessions[user_id] = session
            return escalation_response

        # Normal flow
        if session.get("awaiting_order_id"):
            intent = "order"
        elif session.get("awaiting_refund_reason"):
            intent = "refund"
        else:
            intent = self.intent_recognizer.recognize_intent(user_input)

        handler = self.handler_factory.get_handler(intent)
        response = handler.handle_query(user_input, session, self.query_database, self.backend_manager)
        self.user_sessions[user_id] = session
        return response

# Purpose: to recognize user intent              
class intentRecognizer:
    def __init__(self, query_db):
        self.query_database = query_db # also given the json file 
        # creates a dictinary where the keys are user intent, the values are list of phrases.
        self.intent_synonyms = {
            "order": ["where is my order", "track my package", "where is my package", "when will my order arrive", "has my order shipped"],
            "refund": ["i want to return my order", "i want to return my package", "i want a refund", "i want to return my product", "how do i get a refund", "can i return this", "i need a refund", "refund"],
            "inventory": ["do you have", "is the iphone in stock", "available", "do you sell", "is it in stock", "any deals"],
            "payment": ["why did my payment fail", "payment didn’t go through", "card declined", "i can’t pay", "why isn’t my card working"],
            "live_agent": ["talk to a human", "connect me to a person", "can i speak to someone", "get me a human", "i need help", ],
            "general": ["hello", "hi", "good morning", "help", "customer service", "support"]
            # can add more here
        }

    # Purpose: to recognize user intent based on input and predefined synonyms
    # Contract: recognize_intent(user_input: str) -> str
    def recognize_intent(self, user_input):
        fix = user_input.lower().strip() # remove unecessary character

        # will first try to match with synonyms
        # loop through dictionary and return intent if there is a match
        for intent, phrases in self.intent_synonyms.items():
            for phrase in phrases: # for each phrase in a list of phrases.. 
                if phrase in fix:   # if that phrase is the fixed user input.. 
                    return intent # return key 
                
        # If no synonym, try matching with json questions directly
        for intent in self.query_database.queries:
            section = self.query_database.queries[intent]
            for entry in section:
                question = entry.get("Question", "").lower()
                if question in fix:
                    return intent
            
        # if phrases dont match, return "unrecognized"
        return "unrecognized"

# TESTS AND MAIN 

def test_intent_recognition_basic():
    db = Query_Database("queries.json")
    recognizer = intentRecognizer(db)
    assert recognizer.recognize_intent("Where is my order?") == "order"
    assert recognizer.recognize_intent("I want a refund") == "refund"
    assert recognizer.recognize_intent("Do you sell iPhones") == "inventory"
    assert recognizer.recognize_intent("My card was declined") == "payment"
    assert recognizer.recognize_intent("Talk to a human") == "live_agent"
    assert recognizer.recognize_intent("Hello") == "general"

def test_intent_recognition_edge_cases():
    db = Query_Database("queries.json")
    recognizer = intentRecognizer(db)
    assert recognizer.recognize_intent("") == "unrecognized"
    assert recognizer.recognize_intent("   ") == "unrecognized"
    assert recognizer.recognize_intent("ASDFGHJKL") == "unrecognized"

def test_sentiment_detection_triggers_escalation():
    session = {}
    observer = SentimentObserver()
    response = observer.update("This is ridiculous!", session)
    assert response is not None
    assert session.get("escalate") is True

def test_sentiment_detection_ignores_neutral_input():
    session = {}
    observer = SentimentObserver()
    response = observer.update("How long is shipping?", session)
    assert response is None
    assert session.get("escalate") is None

def test_order_handler():
    db = Query_Database("queries.json")
    handler = OrderHandler()
    backend = backendManager()
    session = {}

    # Step 1: ask for ID
    response = handler.handle_query("Where is my order", session, db, backend)
    assert "can you provide your order id so i can locate your order?" in response.lower()
    assert session.get("awaiting_order_id") is True

    # Step 2: provide order ID
    response = handler.handle_query("12345", session, db, backend)
    assert "order 12345" in response
    assert session.get("awaiting_order_id") is False

def test_refund_handler_simple_flow():
    db = Query_Database("queries.json")
    handler = RefundHandler()
    backend = backendManager()
    session = {}

    # Step 1: initiate refund
    response = handler.handle_query("I want a refund", session, db, backend)
    assert "reason" in response.lower()
    assert session.get("awaiting_refund_reason") is True

    # Step 2: give reason
    response = handler.handle_query("Product is broken", session, db, backend)
    assert "refund request" in response.lower()
    assert session.get("awaiting_refund_reason") is False

def test_query_fallback_logs_unknown(tmp_path):
    # Redirect unrecognized log temporarily
    unknown_file = tmp_path / "unrecognized_queries.txt"
    db = Query_Database("queries.json")
    db.writeUnrecognized = lambda x: unknown_file.write_text(x)

    result = db.lookup_response("orders", "asdfghjkl")
    assert result is None
    assert unknown_file.read_text() == "asdfghjkl"

def test_inventory_handler_prompt():
    db = Query_Database("queries.json")
    handler = InventoryHandler()
    backend = backendManager()
    session = {}

    response = handler.handle_query("I want to buy something", session, db, backend)
    assert "specify the product" in response.lower()


window.geometry("350x520")
window.title("AI Assistance")
photo1 = tk.PhotoImage(file='pikachu.png')

def send_message():
    user_input = input_field.get()  # Get user input from the entry field

    chat_display.tag_config("user_tag", foreground="green", font=("Arial", 10, "bold"))
    chat_display.tag_config("bot_tag", foreground="blue", font=("Arial", 10, "bold"))


    if user_input.strip():  # Ensure input is not empty
        # Display user input in the chat window
        chat_display.config(state=tk.NORMAL)
        chat_display.insert(tk.END, "You: ", "user_tag")
        chat_display.insert(tk.END, f"{user_input}\n")
        chat_display.config(state=tk.DISABLED)
        chat_display.see(tk.END)  # Scroll to the end

        # Process the input with the chatbot
        response = bot.process_input(user_input, user_id="user123")
        
        # Display chatbot response in the chat window
        chat_display.config(state=tk.NORMAL)
        chat_display.insert(tk.END, "Chatbot: ", "bot_tag")
        chat_display.insert(tk.END, f"{response}\n")
        chat_display.config(state=tk.DISABLED)
        chat_display.see(tk.END)  # Scroll to the end

        # Clear the input field
        input_field.delete(0, tk.END)

if __name__ == "__main__":
    # Window logic
    chat_display = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=50, height=20, state=tk.DISABLED)
    chat_display.pack(padx=10, pady=10)

    label = tk.Label(window, text="Type and press 'Enter' to speak with AI assistant", font=('Arial', 10), fg='Black')
    label.pack()

    input_field = tk.Entry(window, width=50)
    input_field.pack(padx=(10, 0), pady=(10, 0))
    input_field.bind("<Return>", lambda event: send_message())

    label2 = tk.Label(window, image=photo1)
    label2.pack()

    # Chatbot code
    query_db = Query_Database("queries.json")
    intent_recognizer = intentRecognizer(query_db)
    backend_manager = backendManager()
    handler_factory = QueryManager  # static factory

    bot = Chatbot(query_db, intent_recognizer, backend_manager, handler_factory)

    # Start the GUI event loop
    window.mainloop()


