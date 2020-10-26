import nltk
import numpy as np
from tqdm import tqdm
from typing import List, Dict, Tuple


class TFIDF:
    def generate(self, corpus: List[Tuple[str, List[str]]]):
        """
        Args:
            corpus List of documents where the first element is the document title, second
            element is an array of words in the document
        """
        self.corpus = corpus
        self.cfd = nltk.ConditionalFreqDist(
            (title, word) for title, words in self.corpus for word in words
        )
        words_in_cfd = set([w for document in self.cfd for w in self.cfd[document]])

        # Map word to an index
        word_lookup_table = {w: i for i, w in enumerate(words_in_cfd)}
        # Map index to a word
        self.vocab = {i: w for i, w in enumerate(words_in_cfd)}

        def calc(cfd):
            df = doc_freq_dict(cfd)
            tfidf = {}
            num_docs = len(cfd)

            # TODO This can be sped up by converting to np arrays
            for document in tqdm(cfd):
                tfidf[document] = np.zeros(len(words_in_cfd))

                for w in df:
                    tf = cfd[document][w] / (len(cfd[document]) + 1)
                    idf = num_docs / (df[w] + 1)
                    word_index = word_lookup_table[w]
                    tfidf[document][word_index] = tf * np.log(idf)

            return tfidf

        # Compute document frequency for each word in CFD
        def doc_freq_dict(cfd):
            df = {}
            for w in tqdm(words_in_cfd):
                for document in cfd:
                    if w in cfd[document]:
                        df[w] = 1 + df.get(w, 0)

            return df

        self.scores = calc(self.cfd)

    # TODO Probably can delete
    def sentence_occurrences(self, word: str):
        """Returns a list of the document titles in which a word occurred in the corpus
        along with the count
        ex: [(title, 1), (title2, 3),...]
        """
        occurrences = [title for title, words in self.cfd.items()]
        occurrences = [(title, self.cfd[title][word]) for title in occurrences]
        return occurrences

    def get_scores(self, title):
        """self.scores is stored as a dict where the key is the title of the document
        and the value is a list of scores.
        Return back a sorted list of all (word, score) in a document given it's title.
        """
        # score_list = [self.scores[title] for title in self.scores.keys()]
        # score_list = np.sum(score_list, axis=0)
        # score_list = [score / occurrences[i] for i, score in enumerate(score_list)]

        score_list = self.scores[title]
        score_tuples = [(self.vocab[i], score) for i, score in enumerate(score_list)]
        score_tuples = sorted(score_tuples, key=lambda x: x[1], reverse=True)

        return score_tuples

    def print_scores(self, start=0, end=10, n=10):
        for title in list(self.scores.keys())[start:end]:
            print(title)
            for word, score in self.get_scores(title=title)[:n]:
                print(word, round(score, ndigits=5))
            print()