import xml.etree.ElementTree as ET
from typing import Iterable
import pickle
from collections import defaultdict
from aspect_based_sentiment_analysis import (
    LabeledExample,
    Sentiment
)


def read_sentences(file):
    """ Read sentences from the XML file which are in the format
    given in the SemEval'14 (http://alt.qcri.org/semeval2014/task4/) """
    return ET.parse(file).getroot().findall('sentence')


def validate_sentences(sentences, stats):
    """ The function protect against processing unlabeled examples (no
    aspect terms). Secondly, it removes aspects with the "conflict" aspect
    polarity. """
    for sentence in sentences:
        # According to documentation is only a single <aspectTerms>
        aspects = sentence.find('aspectCategories') or []

        # An iterator over aspects should be materialized, otherwise the
        # first occurrence of the "conflict" breaks a loop (due to remove).
        for aspect in list(aspects):
            polarity = aspect.attrib['polarity']
            if polarity == 'conflict':
                aspects.remove(aspect)
                stats['conflicts'] += 1

        if not aspects:
            stats['rejected'] += 1
            continue
        yield sentence


def generate_classifier_examples(sentence) -> Iterable[LabeledExample]:
    """ Each labeled sentence can have several aspect terms so we can
    generate several examples. Sentences should be validated before. """
    polarity_to_sentiment = {
        'neutral': Sentiment.neutral,
        'negative': Sentiment.negative,
        'positive': Sentiment.positive,
    }
    text = sentence.find('text').text.lower()
    aspects = sentence.find('aspectCategories')
    for aspect in aspects:
        polarity = aspect.attrib['polarity']
        aspect = aspect.attrib['category'].lower()
        sentiment = polarity_to_sentiment[polarity]
        yield LabeledExample(text, aspect, sentiment)

def save_dataset():
    sentences = read_sentences('./data/semeval/train.xml')
    stats = defaultdict(lambda: 0)
    examples = []
    for sentence in validate_sentences(sentences, stats):
        examples.append(list(generate_classifier_examples(sentence)))
    
    with open('./data/semeval/labeled_train.bin', 'wb') as f:
        pickle.dump(examples, f)
    
if __name__ == "__main__":
    save_dataset()
