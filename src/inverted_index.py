import re

# The Inverted Index can be understood as a simple key/value dictionary 
# where per each term we store a list of appearances of those terms in the documents and their frequency.

# Appearance class represents a single Appearance of a term in a document:
class Appearance:
    """
    Represents the appearance of a term in a given document, along with the
    frequency of appearances in the same one.
    """
    def __init__(self, docId, frequency):
        self.docId = docId
        self.frequency = frequency
        
    def __repr__(self):
        """
        String representation of the Appearance object
        """
        return str(self.__dict__)

# Database class is a fake in-memory DB used to persist the documents after they have been indexed.
class Database:
    """
    In memory database representing the already indexed documents.
    """
    def __init__(self):
        self.db = dict()
    def __repr__(self):
        """
        String representation of the Database object
        """
        return str(self.__dict__)
    
    def get(self, id):
        return self.db.get(id, None)
    
    def add(self, document):
        """
        Adds a document to the DB.
        """
        return self.db.update({document['id']: document})
    def remove(self, document):
        """
        Removes document from DB.
        """
        return self.db.pop(document['id'], None)

# Inverted Index
class InvertedIndex:
    """
    Inverted Index class.
    """
    def __init__(self, db):
        self.index = dict()
        self.db = db
    def __repr__(self):
        """
        String representation of the Database object
        """
        return str(self.index)
        
    def index_document(self, document):
        """
        Process a given document, save it to the DB and update the index.
        """
        # Remove punctuation from the text.
        clean_text = re.sub(r'[^\w\s]','', document['text'])
        terms = clean_text.split(' ')
        appearances_dict = dict()
        # Dictionary with each term and the frequency it appears in the text.
        for term in terms:
            term_frequency = appearances_dict[term].frequency if term in appearances_dict else 0
            appearances_dict[term] = Appearance(document['id'], term_frequency + 1)
            
        # Update the inverted index
        update_dict = { key: [appearance]
                       if key not in self.index
                       else self.index[key] + [appearance]
                       for (key, appearance) in appearances_dict.items() }
        self.index.update(update_dict)
        # Add the document into the database
        self.db.add(document)
        return document
    
    def lookup_query(self, query):
        """
        Returns the dictionary of terms with their correspondent Appearances. 
        This is a very naive search since it will just split the terms and show
        the documents where they appear.
        """
        return { term: self.index[term] for term in query.split(' ') if term in self.index }

if __name__=='__main__':
    # Inverted Index
    db = Database()
    index = InvertedIndex(db)

    # Index the input sentence
    sentence = {'id': '0', 'text': 'sentence has basic cinematography comment which is amazing'}
    index.index_document(sentence)

    # Search new sentence
    result = index.lookup_query('pretty amazing cinematography')

    # Print the results
    for term in result.keys():
        print(f'Word from input sentence: {term} ------------------------')
        for appearance in result[term]:
            document = db.get(appearance.docId)
            print(f'Found in document (Sentence) id: {appearance.docId}')
            print(f'Found in document (Sentence): {document["text"]}')