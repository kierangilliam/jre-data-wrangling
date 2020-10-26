import nltk


class Logger:
    log_info = True

    def info(self, *args):
        if self.log_info:
            print("[INFO]", end=" ")
            self.log(list(args))

    def error(self, *args):
        if self.log_info:
            print("[ERROR]", end=" ")
            self.log(list(args))

    def log(self, args):
        print(" ".join([str(x) for x in args]))


flatten = lambda l: [item for sublist in l for item in sublist]


def clean_text(document: str):
    stopwords = list(nltk.corpus.stopwords.words("english"))
    # TODO If I stem should remove a lot of these
    stopwords.extend(
        [
            "'red",
            "'s",
            "'re",
            "[ ]",
            "[",
            "]",
            "n't",
            "uh",
            "'m",
            "um",
            "like",
            "yeah",
            "__",
            "ve",
            "re",
        ]
    )
    stopwords = set(stopwords)
    words = nltk.tokenize.word_tokenize(document)
    ps = nltk.stem.PorterStemmer()
    words = [
        ps.stem(w.strip().lower()) for w in words if w.strip().lower() not in stopwords
    ]
    # Pad for ConditionalFreqDist to register word so enumerate(...) doesn't shift the indices
    # TODO think of a different way to do this
    return words if len(words) > 0 else ["<BLANK>"]