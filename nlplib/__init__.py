import nltk
nltk.download('maxent_ne_chunker')

texts = [
    """
    Babylon was a significant city in ancient Mesopotamia,
    in the fertile plain between the Tigris and Euphrates rivers.
    """,
    """
    Hammurabi was the sixth Amorite king of Babylon
    from 1792 BC to 1750 BC middle chronology.
    """
]
 
def source(texts, targets):
    for text in texts:
        for t in targets:
            t.send(text)

def coroutine(func):
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr
    return start

@coroutine
def sent_tokenize_pipeline(targets):
    while True:
        text = (yield)
        sentences = nltk.sent_tokenize(text)
        for sentence in sentences:
            for target in targets:
                target.send(sentence)
 
@coroutine
def word_tokenize_pipeline(targets):
    while True:
        sentence = (yield)
        words = nltk.word_tokenize(sentence)
        for target in targets:
            target.send(words)
 
@coroutine
def pos_tag_pipeline(targets):
    while True:
        words = (yield)
        tagged_words = nltk.pos_tag(words)
 
        for target in targets:
            target.send(tagged_words)
 
@coroutine
def ne_chunk_pipeline(targets):
    while True:
        tagged_words = (yield)
        ner_tagged = nltk.ne_chunk(tagged_words)
 
        for target in targets:
            target.send(ner_tagged)

@coroutine
def printer():
    while True:
        line = (yield)
        print(line)

for text in texts:
    sentences = nltk.sent_tokenize(text)
    for sentence in sentences:
        words = nltk.word_tokenize(sentence)
        tagged_words = nltk.pos_tag(words)
        ne_tagged_words = nltk.ne_chunk(tagged_words)
 
@coroutine
def filter_short(min_len, targets):
    while True:
        words = (yield)
        if len(words) < min_len:
            continue
        for target in targets:
            target.send(words)
 

source(texts, targets=[
    sent_tokenize_pipeline(targets=[
        printer(),
        word_tokenize_pipeline(targets=[
            printer(),
            filter_short(10, targets=[ # Filter
                pos_tag_pipeline(targets=[
                    printer(),
                    ne_chunk_pipeline(targets=[printer()]),
                ])
            ])
        ])
    ])
])
 