from chatterbot import ChatBot

# chatterbot setup
chatbot = ChatBot("racerbot94")
chatbot.train("chatterbot.corpus.english")

test = chatbot.get_response("What's your name?")

print test
