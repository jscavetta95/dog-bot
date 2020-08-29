import re


class IntentClassifier:
    def __init__(self):
        pass

    def classify_intent(self, text):
        pass


class SimpleIntentClassifier(IntentClassifier):
    def __init__(self):
        super().__init__()

    def classify_intent(self, text):
        text = text.lower().strip()
        if re.search("hello.*|hi.*", text):
            return 'greeting'
        elif re.search("how are you.*", text):
            return 'how_are_you'
        elif re.search("goodbye.*|bye.*", text):
            return 'quit'
        if 'tell ' in text[0:5] or 'what ' in text[0:5]:
            return 'query'
        elif 'do ' in text[0:3] or 'are ' in text[0:4] or 'does ' in text[0:5] or '?' in text:
            return 'confirm'
        else:
            return 'learn'
