from collections import Counter
import numpy as np
import syllables

class LanguageModel:
    # constants to define pseudo-word tokens
    # access via self.UNK, for instance
    UNK = "<UNK>"

    def __init__(self, n_gram, is_laplace_smoothing, line_begin="<line>", line_end="</line>"):
        """Initializes an untrained LanguageModel
        Parameters:
          n_gram (int): the n-gram order of the language model to create
          is_laplace_smoothing (bool): whether or not to use Laplace smoothing
          line_begin (str): the token designating the beginning of a line
          line_end (str): the token designating the end of a line
        """
        self.line_begin = line_begin
        self.line_end = line_end
        # your other code here
        self.is_laplace_smoothing = is_laplace_smoothing
        self.n_gram = n_gram
        # tokens in current model
        self.tokens = []
        # vocabulary of current model
        self.vocab = {}
        # generated n_grams for current model
        self.n_grams = []
        # total occurences of all n-grams
        self.total_occ = {}
        # total occurences of all n-1 grams
        self.minus_one_occ = {}
        # trained data for current model
        self.trained_data = {}

    def make_ngrams(self, tokens, n):
        """Creates ngrams for the given sentences
        Parameters:
          sentence (list): list of tokens as strings from the training file

        Returns:
          list: list of tuples of strings, each tuple will represent an individual n-grams
        """
        n_grams = [tokens[i:(i + n)] for i in range(len(tokens) - n + 1)]
        return n_grams

    def mle(self, curr_n_gram, total_occ, minus_one_occ):
        """Calculate the MLE for the current input n-gram
        Parameters:
          curr_n_gram (tuples): tuples of string, representing our current n_gram
          total_occ (Counter): a counter dictionary containing the occurences of all n-grams
          minus_one_occ (Counter): a counter dictionary containing the occurences of all n-1 grams
        Returns:
          float: the MLE value of the current n-gram
        """
        # total tokens (N)
        tokens_count = len(self.tokens)
        # vocab size (|V|)
        vocab_size = len(self.vocab)
        # total occurences of current ngrams
        curr_count = total_occ[str(curr_n_gram)]
        # total occurences of current n-1 grams
        minus_one_count = minus_one_occ[str(curr_n_gram[:-1])]
        # calculation for unigram
        if self.n_gram == 1:
            if self.is_laplace_smoothing:
                return (curr_count + 1) / (tokens_count + vocab_size)
            else:
                return curr_count / tokens_count

        # for any n-grams other than unigrams
        if self.is_laplace_smoothing:
            return (curr_count + 1) / (minus_one_count + vocab_size)
        else:
            return curr_count / minus_one_count

    def train(self, sentences):
        """Trains the language model on the given data. Assumes that the given data
        has tokens that are white-space separated, has one sentence per line, and
        that the sentences begin with line_begin and end with line_end
        Parameters:
          sentences (list): list of strings, one string per line in the training file
        Returns:
        None
        """
        # model tokens and vocabulary
        self.tokens = " ".join(sentences).split()
        self.vocab = Counter(self.tokens)
        # replace token that occurs once with unknown tokens
        self.tokens = [token.replace(token, self.UNK) if self.vocab[token] == 1 else token for token in self.tokens]
        # replace vocab that occurs once with unknown tokens
        self.vocab = Counter(self.tokens)

        trained_data = Counter()
        self.n_grams = self.make_ngrams(self.tokens, self.n_gram)
        minus_one_n_grams = self.make_ngrams(self.tokens, self.n_gram - 1)

        # total occurences of all n-grams
        self.total_occ = Counter(str(n_gram) for n_gram in self.n_grams)
        # total occurences of all n-1 grams
        self.minus_one_occ = Counter(str(n_gram) for n_gram in minus_one_n_grams)
        # iterate through model n-grams to calculate probability
        for n_gram in self.n_grams:
            trained_data[tuple(n_gram)] = self.mle(n_gram, self.total_occ, self.minus_one_occ)
        self.trained_data = trained_data

    def score(self, sentence):
        """Calculates the probability score for a given string representing a single sentence.
        Parameters:
          sentence (str): a sentence with tokens separated by whitespace to calculate the score of

        Returns:
          float: the probability value of the given string for this model
        """
        # current sentence tokens (replace with unknown token if word is not in vocabulary) and n-grams
        sentence_tokens = sentence.split()
        sentence_tokens = [token.replace(token, self.UNK) if token not in self.vocab else token for token in
                           sentence_tokens]
        sentence_n_grams = self.make_ngrams(sentence_tokens, self.n_gram)
        # if probability is not zero we obtain, else we recalculate mle for the current unseen n-gram
        probs = [self.trained_data[tuple(n_gram)] if self.trained_data[tuple(n_gram)] != 0 else self.mle(n_gram,
                                                                                                         self.total_occ,
                                                                                                         self.minus_one_occ)
                 for n_gram in sentence_n_grams]
        # chain rule to multiply all probabilities
        return np.exp(np.sum(np.log(probs)))

    def get_next_word(self, curr_token):
        """Gets the next word for sentence generation.
        Parameters:
          curr_token (tuples): tuples of string, representing n-grams consisting our last n-1 tokens in our generated sentence so far

        Returns:
          string: the next word for our generated sentence
        """
        # finding possible n-grams
        possible_n_grams = {}
        if self.n_gram == 1:
            possible_n_grams = self.trained_data
        else:
            for k, v in self.trained_data.items():
                # find list of n-grams that has a prefix matching our current n-gram
                n_minus_one_k = list(k[:-1])
                if n_minus_one_k == curr_token:
                    possible_n_grams[k] = v

        possible_words = list(possible_n_grams.keys())
        probs = list(possible_n_grams.values())
        # normalize probabilities and get index
        random_choice = np.random.choice(len(possible_words), p=probs / np.sum(probs))
        # get the last word from the selected n-gram as our next word
        next_word = possible_words[random_choice][-1]
        return next_word
    
    
    def generate_haiku(self, n):
        """Generates n haikus from a trained language model
        Parameters:
          n (int): the number of haikus to generate

        Returns:
          list: a list containing strings, one per generated sentence
        """
        haikus = []
        if self.n_gram == 1:
            self.trained_data.pop(tuple([self.line_begin]))
        while n > 0:
            haiku = []
            haiku.append(self.generate_line(5).split(self.line_begin)[-1])
            haiku.append(self.generate_line(7).split(self.line_begin)[-1])
            haiku.append(self.generate_line(5).split(self.line_begin)[-1])
            haikus.append(haiku)
            n -= 1
        return haikus

    def generate_line(self, syllable_limit):
        """Generates a single line from a trained language model

        Returns:
          string: the generated line
        """
        count_syllables = 0
        # initialize resulting sentence with line begin token depending on the number of n
        if self.n_gram == 1:
            sentence = [self.line_begin]
        else:
            sentence = [self.line_begin] * (self.n_gram - 1)

        next_word = ""
        # while syllable count has not reached limit
        while count_syllables != syllable_limit:
            curr_token = sentence[-(self.n_gram - 1):]
            next_word = self.get_next_word(curr_token)
            new_count = syllables.estimate(next_word) + count_syllables

            if next_word not in [self.line_begin, self.line_end, self.UNK] and (new_count <= syllable_limit):
                sentence.append(next_word)
                count_syllables = new_count
            else:
                # to prevent long computation
                sentence = sentence[:(self.n_gram-1)] if self.n_gram > 1 else sentence[:self.ng_gram]
                count_syllables = 0

        # for n > 2 case, we n - 2 append line ends at end of the sentence, as we have appended one in the previous while loop.
        # In total, we will have n - 1 line ends.
        if self.n_gram > 2:
            for _ in range(self.n_gram - 2):
                sentence.append(self.line_end)
        return ' '.join(sentence)