#coding: utf-8


if __name__ == "__main__":
    

    from gensim.models import KeyedVectors
    import tensorflow as tf
    import re
    import numpy as np
    
    def get_word_vec(word_vectors, token):
        """Helper method to retrieve pretrained word emb"""
        
        try:
            if token in word_vectors:
                word_vector = word_vectors[token]
            elif token.lower() in word_vectors:
                word_vector = word_vectors[token.lower()]
            elif re.sub(r'\d', '#', token.lower()) in word_vectors:
                word_vector = word_vectors[re.sub(r'\d', '#', token.lower())]
            elif re.sub(r'\d', '0', token.lower()) in word_vectors:
                word_vector = word_vectors[re.sub(r'\d', '0', token.lower())]
            else:
                word_vector = np.zeros(word_vectors.vector_size, dtype='float')        
            return word_vector        
    
        except KeyError:
            print("Key not found and bug in logic")
    
    
    def load_data(n):
        with open(file, 'rt') as f:
            
    vocab = set(["<unk>", "<pad>"])
    word_to_idx = {"<unk>": 0, "<pad>": 1}
    sents = []
    labels = []
    sent_lens = []
    with open(file, 'rt') as f:
        sent = []
        sent_labels = []
        for line in f:
            if line == "\n":
                sents.append(sent)
                sent = []
                sent_labels = []
            token, pos, ner = line.split()
            
            # word-level info
            if token not in vocab:
                vocab[token] = token
                word_to_idx[token] = len(vocab)
            sent_labels.append(ner)
                
                    
    word_vectors = KeyedVectors.load_word2vec_format("german.model", binary=True)
    print("Vector size of model ", word_vectors.vector_size)
    #print(get_word_vec(word_vectors, "Frau"))
    #print(get_word_vec(word_vectors, "Vereinigten_Staaten"))    
    #print(get_word_vec(word_vectors, "blah"))
    
    
    
    graph = tf.Graph()
    graph.seed
    session = tf.Session(graph=graph, config=tf.ConfigProto(log_device_placement=False))
    
    with session.graph.as_default():
        
        tags = tf.placeholder(tf.float32, [None, None], name="tags")
        emb_size = word_vectors.vector_size
        embedded_inputs = tf.placeholder(tf.float32, [None, None, emb_size], name="embedded_inputs")
    
    
    n_epochs = 25
    for n in range(5,100):
        for epoch in n_epochs:
            pass
        
        
        
        
    
    
    