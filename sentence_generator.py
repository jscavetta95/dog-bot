import inflect
import pandas as pd

p = inflect.engine()

special_case_nouns = ['mammal']


def sentence_generator(triples, nlp):
    sentences = []

    triples = [{'subject': triple.subject.label, 'predicate': triple.predicate,
                'object': triple.object.label if triple.object else ''} for triple in triples]
    df = pd.DataFrame(triples)
    for combination in df[['subject', 'predicate']].drop_duplicates().itertuples(index=False):
        sentence = [f"{p.plural_noun(combination.subject).title()} "]
        if combination.predicate == 'be':
            sentence.append('are ')
        else:
            sentence.append(f"{combination.predicate} ")

        for obj_label in df.object[(df.subject == combination.subject) & (df.predicate == combination.predicate)]:
            if obj_label == '':
                continue

            doc = nlp(' '.join([combination.subject, combination.predicate, obj_label]))
            if doc[2].pos_ in ['NOUN', 'VERB'] or doc[2].text in special_case_nouns:
                sentence.append(f'{p.plural_noun(doc[2].text)}, ')
            else:
                sentence.append(f'{p.plural_adj(doc[2].text)}, ')

        sentence[len(sentence) - 1] = sentence[len(sentence) - 1].replace(', ', '.')
        if len(sentence) == 4:
            sentence[len(sentence) - 2] = sentence[len(sentence) - 2].replace(', ', ' and ')
        elif len(sentence) > 4:
            sentence.insert(len(sentence) - 1, 'and ')
        sentences.append(str.join('', sentence))

    return sentences
