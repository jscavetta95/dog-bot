from intent import IntentClassifier
from knowledge import KnowledgeBase
from sentence_generator import sentence_generator


class DogBot:
    def __init__(self, knowledge_base: KnowledgeBase, intent_classifier: IntentClassifier, debug):
        self.knowledge = knowledge_base
        self.intent_classifier = intent_classifier
        self.actions = {'learn': self.learn_relationship, 'query': self.query_relationships,
                        'confirm': self.confirm_relationship, 'quit': self.finish_conversation,
                        'greeting': self.greet, 'how_are_you': self.feeling}
        self.debug = debug

    def conversate(self):
        print('Hello! I am Dog Bot.')
        done = False
        while not done:
            input_text = input()
            input_text = input_text[0].upper() + input_text[1:]
            action = self.intent_classifier.classify_intent(input_text)
            done = self.actions[action](input_text)

        exit()

    def learn_relationship(self, text):
        subject_label, predicate, object_label = self.__parse_keywords(text)

        if subject_label and predicate:
            if object_label:
                print(f'Do you want me to learn that {subject_label.text.lower()} {predicate.text.lower()} '
                      f'{object_label.text.lower()}?')
            else:
                print(f'Do you want me to learn that {subject_label.text.lower()} {predicate.text.lower()}?')

            ans = input()
            if ans.strip().lower() == 'yes':
                self.knowledge.add_triple(subject_label, predicate, object_label)
                print("Okay, got it.")
            else:
                print("Okay, I won't learn that.")
        else:
            self.__do_not_understand()

        self.__debug_sentence(text)
        return False

    def query_relationships(self, text):
        subject_label, _, _ = self.__parse_keywords(text)

        if subject_label:
            triples = self.knowledge.retrieve_triples(subject_label)
            if triples:
                sentences = sentence_generator(triples, self.knowledge.nlp)
                print(str.join(' ', sentences))
            else:
                print(f"I don't know anything about {subject_label.text.lower()}, maybe you could teach me?")
        else:
            self.__do_not_understand()

        self.__debug_sentence(text)
        return False

    def confirm_relationship(self, text):
        subject_label, predicate, object_label = self.__parse_keywords(text)

        if subject_label and predicate:
            exists = self.knowledge.find_triple(subject_label, predicate, object_label)
            if exists:
                if object_label:
                    print(f'Yes, {subject_label.text.lower()} {predicate.text.lower()} {object_label.text.lower()}.')
                else:
                    print(f'Yes, {subject_label.text.lower()} {predicate.text.lower()}.')
            else:
                if object_label:
                    print(f"No, I don't think {subject_label.text.lower()} {predicate.text.lower()} "
                          f"{object_label.text.lower()}.")
                else:
                    print(f"No, I don't think {subject_label.text.lower()} {predicate.text.lower()}.")
                print("If you disagree, you should teach me.")
        else:
            self.__do_not_understand()

        self.__debug_sentence(text)
        return False

    @staticmethod
    def greet(_):
        print('Hello! Ask me or teach me something.')

    @staticmethod
    def feeling(_):
        print('I am doing great! Feel free to ask me or teach me something.')

    def __parse_keywords(self, text):
        tokens = self.knowledge.nlp(text)
        subject_token = self.__find_subject(tokens)
        if not subject_token:
            return None, None, None

        predicate_token = self.__find_predicate(tokens, subject_token)
        if not predicate_token:
            return subject_token, None, None

        object_token = self.__find_object(tokens, subject_token)
        return subject_token, predicate_token, object_token

    @staticmethod
    def __do_not_understand():
        print("I couldn't figure out what you said. Sorry.")

    def __debug_sentence(self, text):
        if self.debug:
            print("Would you like to see what I read?")
            ans = input()
            if ans.lower() == 'yes':
                print(f"Here is what I found:")
                for token in self.knowledge.nlp(text):
                    print("\t", token.text, "\t", token.pos_, "\t", token.dep_)
            else:
                print("Okay, no problem.")

    @staticmethod
    def finish_conversation(_):
        print('Are you sure you are done chatting?')
        ans = input()
        if ans.lower() == 'yes':
            print("Okay, talk to you later.")
            return True
        else:
            print("Sure, let's keep chatting.")
            return False

    @staticmethod
    def __find_subject(tokens):
        for token in tokens:
            if token.dep_ == 'nsubj' and not token.is_stop:
                return token

        for token in tokens:
            if token.dep_ == 'pobj' and token.head.lemma_ == 'about' and not token.is_stop:
                return token

        for token in tokens:
            if token.pos_ == 'NOUN' and not token.is_stop:
                return token

        for token in tokens:
            if token.dep_ == 'acomp' and token.head.lemma_ == 'be' and not token.is_stop:
                return token

        return None

    @staticmethod
    def __find_object(tokens, subject):
        best_object = None
        for token in tokens:
            if token.dep_ in ['dobj', 'acomp', 'advmod', 'attr', 'pobj'] and token.i != subject.i:
                if best_object is None or (token.pos_ == 'ADJ' and best_object.pos_ == 'ADV'):
                    best_object = token

        return best_object

    @staticmethod
    def __find_predicate(tokens, subject):
        for token in tokens:
            if token.dep_ == 'ROOT' and token.i != subject.i:
                return token

        for token in tokens:
            if token.text.lower() == 'like':
                return token

        return None
