import numpy as np

class MorphoDataset:
    """Class capable of loading morphological datasets in vertical format.

    The dataset is assumed to be composed of factors (by default FORMS, LEMMAS and TAGS),
    each an object containing the following fields:
    - strings: Strings of the original words.
    - word_ids: Word ids of the original words (uses <unk> and <pad>).
    - words_map: String -> word_id map.
    - words: Word_id -> string list.
    - alphabet_map: Character -> char_id map.
    - alphabet: Char_id -> character list.
    - charseq_ids: Character_sequence ids of the original words.
    - charseqs_map: String -> character_sequence_id map.
    - charseqs: Character_sequence_id -> [characters], where character is an index
        to the dataset alphabet.
    """
    FORMS = 0
    LEMMAS = 1
    TAGS = 2
    FACTORS = 3

    class _Factor:
        def __init__(self, train=None):
            self.words_map = train.words_map if train else {'<pad>': 0, '<unk>': 1}
            self.words = train.words if train else ['<pad>', '<unk>']
            self.word_ids = []
            self.alphabet_map = train.alphabet_map if train else {'<pad>': 0, '<unk>': 1, '<bow>': 2, '<eow>': 3}
            self.alphabet = train.alphabet if train else ['<pad>', '<unk>', '<bow>', '<eow>']
            self.charseqs_map = {'<pad>': 0}
            self.charseqs = [[self.alphabet_map['<pad>']]]
            self.charseq_ids = []
            self.strings = []
            self.index_to_word = []

    def __init__(self, filename, filename_neg=None, train=None, shuffle_batches=True, max_sentences=None, add_bow_eow=False, lowercase=False):
        """Load dataset from file in vertical format.

        Arguments:
        add_bow_eow: Whether to add BOW/EOW characters to the word characters.
        train: If given, the words and alphabets are reused from the training data.
        """

        # Create alphabet map
        self._alphabet_map = train._alphabet_map if train else {'<pad>': 0, '<unk>': 1, '<bow>': 2, '<eow>': 3}
        self._alphabet = train._alphabet if train else ['<pad>', '<unk>', '<bow>', '<eow>']

        # Create word maps
        self._factors = []
        for f in range(self.FACTORS):
            self._factors.append(self._Factor(train._factors[f] if train else None))

        # Load sents
        self.load_sents(filename) # pos examples
        if filename_neg:
            self.load_sents(filename_neg)
        
        #print(self._factors[0].charseqs[:10])
        #print(self._factors[0].charseq_ids[:2])        
        # Compute sentence lengths
        sentences = len(self._factors[self.FORMS].word_ids)
        self._sentence_lens = np.zeros([sentences], np.int32)
        for i in range(len(self._factors[self.FORMS].word_ids)):
            self._sentence_lens[i] = len(self._factors[self.FORMS].word_ids[i])

        self._shuffle_batches = shuffle_batches
        self._permutation = np.random.permutation(len(self._sentence_lens)) if self._shuffle_batches else np.arange(len(self._sentence_lens))


    def load_sents(self, file):
        
        # Load the sentences
        with open(filename, "r", encoding="utf-8") as file:
            in_sentence = False
            for line in file:
                line = line.rstrip("\r\n")
                if line:
                    
                    #line = line.lower()
                    columns = line.split("\t")
                    for f in range(self.FACTORS):
                        factor = self._factors[f]
                        if not in_sentence:
                            factor.word_ids.append([])
                            factor.charseq_ids.append([])
                            factor.strings.append([])
                        word = columns[f] if f < len(columns) else '<pad>'
                        factor.strings[-1].append(word)

                        # Character-level information
                        if word not in factor.charseqs_map:
                            factor.charseqs_map[word] = len(factor.charseqs) # word to int (rank) of word in V
                            factor.charseqs.append([]) # list of list of <charseqs> of type int [1,3,4,...]
                            if add_bow_eow:
                                factor.charseqs[-1].append(factor.alphabet_map['<bow>'])
                            for c in word:
                                #if lowercase and f == self.FORMS: # added lc
                                    #c = c.lower()
                                if c not in factor.alphabet_map:  # this will add the new chars to map/list of letters
                                    if train:
                                        c = '<unk>'
 
    @property
    def sentence_lens(self):
        return self._sentence_lens

    @property
    def factors(self):
        """Return the factors of the dataset.

        The result is an array of factors, each an object containing:
        strings: Strings of the original words.
        word_ids: Word ids of the original words (uses <unk> and <pad>).
        words_map: String -> word_id map.
        words: Word_id -> string list.
        alphabet_map: Character -> char_id map.
        alphabet: Char_id -> character list.
        charseq_ids: Character_sequence ids of the original words.
        charseqs_map: String -> character_sequence_id map.
        charseqs: Character_sequence_id -> [characters], where character is an index
          to the dataset alphabet.
        """

        return self._factors

    def next_batch(self, batch_size, including_charseqs=False):
        """Return the next batch.

        Arguments:
        including_charseqs: if True, also batch_charseq_ids, batch_charseqs and batch_charseq_lens are returned

        Returns: (sentence_lens, batch_word_ids[, batch_charseq_ids, batch_charseqs])
        sequence_lens: batch of sentence_lens
        batch_word_ids: for each factor, batch of words_id
        batch_charseq_ids: For each factor, batch of charseq_ids
          (the same shape as words_id, but with the ids pointing into batch_charseqs).
          Returned only if including_charseqs is True.
        batch_charseqs: For each factor, all unique charseqs in the batch,
          indexable by batch_charseq_ids. Contains indices of characters from self.alphabet.
          Returned only if including_charseqs is True.
        batch_charseq_lens: For each factor, length of charseqs in batch_charseqs.
          Returned only if including_charseqs is True.
        """

        batch_size = min(batch_size, len(self._permutation))
        batch_perm = self._permutation[:batch_size]
        self._permutation = self._permutation[batch_size:]
        return self._next_batch(batch_perm, including_charseqs)

    def epoch_finished(self):
        if len(self._permutation) == 0:
            self._permutation = np.random.permutation(len(self._sentence_lens)) if self._shuffle_batches else np.arange(len(self._sentence_lens))
            return True
        return False

    def _next_batch(self, batch_perm, including_charseqs):
        batch_size = len(batch_perm)

        # General data
        batch_sentence_lens = self._sentence_lens[batch_perm]
        max_sentence_len = np.max(batch_sentence_lens)

        # Word-level data
        batch_word_ids = []
        #batch_strings = [] # added to return string repr
        for factor in self._factors:
            batch_word_ids.append(np.zeros([batch_size, max_sentence_len], np.int32))
            #batch_strings.append([])
            for i in range(batch_size):
                batch_word_ids[-1][i, 0:batch_sentence_lens[i]] = factor.word_ids[batch_perm[i]]
                #batch_strings[-1].append(factor.strings[batch_perm[i]]) # added strings for all factors
        if not including_charseqs:
            #return self._sentence_lens[batch_perm], batch_word_ids, batch_strings # added last
            return self._sentence_lens[batch_perm], batch_word_ids # added last

        # Character-level data
        batch_charseq_ids, batch_charseqs, batch_charseq_lens = [], [], []
        for factor in self._factors:
            batch_charseq_ids.append(np.zeros([batch_size, max_sentence_len], np.int32))
            charseqs_map = {}
            charseqs = []
            charseq_lens = []
            for i in range(batch_size):
                for j, charseq_id in enumerate(factor.charseq_ids[batch_perm[i]]):
                    if charseq_id not in charseqs_map:
                        charseqs_map[charseq_id] = len(charseqs)
                        charseqs.append(factor.charseqs[charseq_id])
                    batch_charseq_ids[-1][i, j] = charseqs_map[charseq_id]

            batch_charseq_lens.append(np.array([len(charseq) for charseq in charseqs], np.int32))
            batch_charseqs.append(np.zeros([len(charseqs), np.max(batch_charseq_lens[-1])], np.int32))
            for i in range(len(charseqs)):
                batch_charseqs[-1][i, 0:len(charseqs[i])] = charseqs[i]

        #return self._sentence_lens[batch_perm], batch_word_ids, batch_charseq_ids, batch_charseqs, batch_charseq_lens, batch_strings # added last
        return self._sentence_lens[batch_perm], batch_word_ids, batch_charseq_ids, batch_charseqs, batch_charseq_lens
