# Problem ------------------------------------------------------
# For a given sentence pair a most relavent sentence.
#
# Reference
# https://www.youtube.com/watch?v=3pRgZfjTb0c
# https://drive.google.com/file/d/1ZzM3uVmR6td0JQ9QfLs7Z0zYR2F4dCln/view 
#
# Approach
# 1. For a Dataset with list of sentences, generate an inverted index,
# For a given word find all sentences containing that word and its number of occurenace
# 2. For a given sentence, get a union of all sentences corresponding to each word in given sentence.
# 3. Calculate Sentence Similarity
# 
# Design 
# Elastic search DB fits well for our problem statement. 
# ES has capability of inverted index and TF-IDF based sentence vectorizer with faster search.
# Semantic Simliratity
#### Generate vectors for each sentence (of length 512 for e.g.)
#### Similarity (Sent1, Sent2) = Similarity(vector(Sent1), vector(Sent2))
#### Similarity(vector1, vector2) = Euclidean_Distance(vector1, vector2) or use Cosine Similarity
######## Lower the Distance, higher the Similararity.
#### BERT or Universal Sentence Encoder (USE) are text encoders that already have  
#### Called as `Nearest Neighbour Search` problem (latest search of Elastic search has already implemented Nearest Neighbour Search)
#### Hence the final search would be Keyword + Vector (Nearest Neighbour) on ES returning ranked set of relevant sentences

DATA_PATH = '/Users/shiv/Documents/gitRepositories/iutils/input/data/IMDB Dataset.csv'

import pandas as pd
from tqdm import tqdm

if __name__=='__main__':
    # Read the dataset and retrieve sentences
    data = pd.read_csv(DATA_PATH)['review'].head(10000)

    # Create a sentence id (document id) created for each of the sentence
    # In our case, convert the index into id
    data = data.reset_index()
    data = data.rename(columns = {'index': 'id'}, inplace = False)
    data['id']= data['id'].astype(str)
    data = data.rename(columns = {'review': 'text'}, inplace = False)
    data['text']= data['text'].apply(lambda x: x.split('.')[0])

    # print(data.head())

    # Inverted Index
    db = Database()
    index = InvertedIndex(db)
    for i in tqdm(data.index):
        sentence = {'id': data.loc[i]['id'], 'text': data.loc[i]['text']}
        index.index_document(sentence)

    # Search new sentence
    result = index.lookup_query('pretty amazing cinematography')

    # Print the results
    for term in result.keys():
        print(f'{term} ------------------------')
        for appearance in result[term]:
            document = db.get(appearance.docId)
            print(appearance.docId)
            print(document['text'])