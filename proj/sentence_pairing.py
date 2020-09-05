#region Problem ------------------------------------------------------
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
#
# Requirements
# pip3 install --upgrade pip
# pip3 install elasticsearch
# pip3 install pandas
# pip3 install --upgrade --no-cache-dir tensorflow
# pip3 install --upgrade tensorflow-hub

#endregion

from elasticsearch import Elasticsearch
import tensorflow as tf
import tensorflow_hub as hub

import pandas as pd
from tqdm import tqdm


def get_data(data_path: str, text_column: str):
    # Read the dataset and retrieve sentences
    data = pd.read_csv(data_path)
    data[text_column] = data[text_column].apply(lambda x: x.split('.')[0])

    return data

def db_setup(hostname: str, port: int):
	# connect to ES on localhost on port 9200
	es = Elasticsearch([{'host': hostname, 'port': port}])
	if es.ping():
		print('Connected to ES!')
	else:
		print('Could not connect!')

	# index in ES = DB in an RDBMS
	# Read each question and index into an index called questions
	# Define the index

	# Refer: https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html
	# Mapping: Structure of the index
	# Property/Field: name and type  
	b = {"mappings": {
            "properties": {
                    "title": {
                        "type": "text"
                    },
                    "title_vector": {
                        "type": "dense_vector",
                        "dims": 512
                }
            }
		}
	}

	ret = es.indices.create(index='sentences-index', ignore=400, body=b) # 400 caused by IndexAlreadyExistsException, 
	print(json.dumps(ret,indent=4))

	# TRY this in browser: http://localhost:9200/questions-index

def db_connect(hostname: str, port: int):
    # connect to ES on localhost on port 9200
	es = Elasticsearch([{'host': hostname, 'port': port}])
	if es.ping():
		print('Connected to ES!')
	else:
		print('Could not connect!')
	return es

def db_insert(database, sentence_id: int, sentence: str, sentence_vector: list()):
	b = {
            "title":sentence,
		    "title_vector":sentence_vector
		}	
	database.index(index="sentences-index", id=sentence_id, body=b)
	# View details: http://localhost:9200/questions-index/_stats?pretty
    # View a document: http://localhost:9200/questions-index/_doc/1

def encode(encoder, text):
    embeddings = tf.make_ndarray(tf.make_tensor_proto(encoder([text]))).tolist()[0]

    # Return a vector of 512 dimensions as a list
    return embeddings

def insert_encoded_data_to_db(database, data, text_column):
    # Encode and insert sentence ID, sentence and it's vector in Database
    for index, row in tqdm(data.iterrows()):
        sentence = row[text_column]
        sentence_vector = encode(_encoder, sentence)
        sentence_id = index
        db_insert(es, sentence_id, sentence, sentence_vector)

def search_by_keyword(database, sentence):
    # Search by Keywords
    b=  {
            'query':{
                'match':{
                    "title":sentence
                }
            }
        }

    res= database.search(index='sentences-index',body=b)
    print("Keyword Search:\n")
    scores = list()
    for hit in res['hits']['hits']:
        print(str(hit['_score']) + "\t" + hit['_source']['title'] )
        scores.append(hit['_score'])
    
    import numpy as np
    print(scores)
    print([score/np.max(scores) for score in scores])

    print("*********************************************************************************");

    return

def search_by_vector(database, query_vector):
    # Search by Vector Similarity
    b = {
            "query": {
                "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'title_vector') + 1.0",
                    "params": {"query_vector": query_vector}
                }
            }
        }
    }

    # print(json.dumps(b,indent=4))
    res= database.search(index='sentences-index', body=b)

    print("Semantic Similarity Search:\n")
    for hit in res['hits']['hits']:
        print(str(hit['_score']) + "\t" + hit['_source']['title'] )

    print("*********************************************************************************");


if __name__=='__main__':
    # CONSTANTS  

    ## DATA
    DATA_PATH = '/Users/shiv/Documents/gitRepositories/iutils/input/data/IMDB Dataset.csv'
    TEXT_COLUMN = 'review'

    ## DATABASE
    DB_HOST_NAME = 'localhost'
    DB_PORT = 9201

    ENCODER_PATH = 'https://tfhub.dev/google/universal-sentence-encoder-large/5'

    # Load the data
    # data = get_data(DATA_PATH, TEXT_COLUMN)

    # Load the encoder
    _encoder = hub.load(ENCODER_PATH)

    # Setup Database
    # db_setup(hostname=DB_HOST_NAME, port=DB_PORT)

    # Connect Database
    db = db_connect(hostname=DB_HOST_NAME, port=DB_PORT)

    # Insert text and encoded text to Database
    # insert_encoded_data_to_db(db, data, TEXT_COLUMN)
    
    # Search new text
    text_to_search = 'pretty amazing movie'
    search_by_keyword(db, text_to_search)
    search_by_vector(db, encode(_encoder, text_to_search))