import spacy

from dog_bot import DogBot
from intent import SimpleIntentClassifier
from knowledge import KnowledgeBase

if __name__ == '__main__':
    nlp = spacy.load("en_core_web_sm")
    knowledge = KnowledgeBase('dog.db', nlp)
    intent_classifier = SimpleIntentClassifier()
    dog_bot = DogBot(knowledge, intent_classifier, debug=False)
    dog_bot.conversate()
