print("memory.py started")
chat_history = []

def save_message(message):
    chat_history.append(message)

def get_history():
    return chat_history


if __name__ == "__main__":

    save_message("show sales")

    print(get_history())



#Follow-up questions
#Conversation memory