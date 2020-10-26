from typing import List, Tuple
from .utils import flatten, Logger
import numpy as np
from tqdm import tqdm
from sklearn.neighbors.kde import KernelDensity
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
from copy import deepcopy
from .Episode import Episode, Caption


class WordVecFactory:
    def __init__(self, captions: List[List[str]]):
        """Args:
        captions (List[List[str]]): Cleaned version of the captions
        (if the word in the create function is also the 'cleaned' version)
        """
        self.captions = captions

    def create(self, word: str):
        return WordVec(
            [word],
            len(self.captions),
            [i for i, words in enumerate(self.captions) if word in words],
        )


class WordVec:
    def __init__(self, words: List[str], text_length: int, indices: List[int]):
        self.words = words
        self.indices = indices
        self.text_length = text_length

    def as_sparse(self):
        return [i if i in self.indices else 0 for i in range(self.text_length)]


class TopicSegmenter:
    captions: List[Caption]
    clusters: List[WordVec]
    Log = Logger()

    def __init__(self, word_vecs, captions):
        self.word_vecs = word_vecs
        self.captions = captions

    def cluster(self, kernel="gaussian", bandwidth=100, plot=None):
        if plot:
            self.kde_cluster(self.word_vecs[plot], kernel, bandwidth, plot=True)

        self.clusters = flatten(
            [self.kde_cluster(v, kernel, bandwidth) for v in self.word_vecs]
        )

    def kde_cluster(self, vec: WordVec, kernel="gaussian", bandwidth=100, plot=False):
        """
        Uses KDE to create clusters out of word vecs
        """
        # TODO Deep copy?
        X = [i for i in vec.indices]
        X = [np.array([idx]) if idx > 0 else [-1] for i, idx in enumerate(X)]
        X = np.array(X).flatten()
        X = X.reshape(-1, 1)

        # TODO There is probably bias at the boundaries, should mirror X
        kde = KernelDensity(kernel=kernel, bandwidth=bandwidth).fit(X)
        s = np.linspace(0, vec.text_length)
        e = kde.score_samples(s.reshape(-1, 1))

        # Reshape back to a 1 by N array
        X = X.reshape(1, -1)

        minima = argrelextrema(e, np.less)[0]
        # Use the linspace to convert back into word indexes
        minima = [s[m] for m in minima]
        # (0, minima 1), (minima 1, minima 2), ... (minima n-1, minima n), (minima n, end)
        minima_pairs = list(zip(np.insert(minima, 0, 0), np.append(minima, s[-1])))

        clusters = [
            np.unique(X[np.logical_and(X >= m1, X < m2)]) for m1, m2 in minima_pairs
        ]

        clusters = [
            WordVec(vec.words, vec.text_length, cluster)
            for cluster in clusters
            if len(cluster) > 0
        ]

        if plot:
            title = " ".join(vec.words)
            plt.plot(s, e)
            plt.title(title)
            plt.show()
            self.Log.info(f"{title}... Number of clusters: {len(clusters)}")
            self.Log.info(f"Original {len(vec.indices)}")
            for c in clusters:
                self.Log.info("\t", len(c.indices), c.indices)

        return clusters

    def condense(self):
        result = deepcopy(self.clusters)
        num_added, i = np.Infinity, 0

        while num_added > 0:
            result, num_added = self.condenser(result)
            i += 1
            if i > 100:
                self.Log.error(
                    "Something went wrong when condensing, iterations reached 100"
                )
                break

        self.condensed = result

    def condenser(self, clusters: List[WordVec], overlap=0.75):
        combined = []
        # Keep track of what clusters we have already combined into a different cluster
        closed_list = []
        num_added = 0

        for i, wc in enumerate(clusters):
            combined.append(None)

            if i in closed_list:
                continue

            # Copy values into new arrays
            words = [w for w in wc.words]
            cluster = np.array([c for c in wc.indices])
            cluster_extent = (np.min(cluster), np.max(cluster))

            # TODO maybe deepcopy?
            combined[i] = WordVec(words, len(self.captions), cluster)
            closed_list.append(i)

            for ii, swc in enumerate(clusters):
                if ii <= i or ii in closed_list:
                    continue

                # Copy values into new arrays
                sub_cluster_words = [w for w in swc.words]
                sub_cluster = np.array([c for c in swc.indices])

                # If both of the lengths are 0 (single dot) then fully/partially contained
                # statement evaluate as True. That is only okay if both clusters contain
                # the same one index
                if (
                    np.max(cluster) - np.min(cluster) == 0
                    and np.max(sub_cluster) - np.min(sub_cluster) == 0
                    and cluster[0] != sub_cluster[0]
                ):
                    continue

                sub_cluster_extent = (np.min(sub_cluster), np.max(sub_cluster))
                partially_contained = is_partially_contained(
                    cluster_extent, sub_cluster_extent, overlap
                )
                # Sub cluster falls completely inside cluster
                fully_contained = is_fully_contained(cluster_extent, sub_cluster_extent)

                # TODO Do I need the `and sub_cluster_length <= length`?
                # (partially_contained and sub_cluster_length <= length)
                if fully_contained or partially_contained:
                    cluster = np.unique(np.hstack((combined[i].indices, sub_cluster)))
                    combined[i].indices = cluster
                    combined[i].words.extend(sub_cluster_words)
                    combined[i].words = list(set(combined[i].words))

                    closed_list.append(ii)
                    num_added += 1

        combined = [wv for wv in combined if wv is not None]
        # Sort by time
        combined = sorted(combined, key=lambda x: np.min(x.indices))

        return combined, num_added

    def get_timestamps(self):
        def to_timestamp(caption, end=False):
            seconds = caption.start + caption.duration if end else caption.start
            minutes = f"{round(seconds / 60 % 60)}"
            minutes = minutes.zfill(2)
            return f"{round(seconds / 60 // 60)}:{minutes}"

        caption_clusters = []
        for wv in self.condensed:
            start, end = np.min(wv.indices), np.max(wv.indices)
            start_t = to_timestamp(self.captions[start])
            end_t = to_timestamp(self.captions[end])
            caption_clusters.append((f"{start_t}-{end_t}", self.captions[start:end]))

        return caption_clusters


class TopicSegmenterVisualizer:
    def __init__(self, topics: TopicSegmenter):
        self.topics = topics

    def print(self, word_vecs: List[WordVec]):
        for i, wv in enumerate(word_vecs):
            start, end = np.min(wv.indices), np.max(wv.indices)
            print(i, f"{start}-{end}", " ".join(wv.words[:10]))
            print(" =========== ")
            captions = [c.text for c in self.topics.captions[start:end]]
            print(" ".join(captions), end="\n\n")

    def plot_clusters(self):
        items = {}
        color_idx = {}

        # Group clusters by word
        for cluster in self.topics.clusters:
            key = " ".join(cluster.words)
            vec = cluster.as_sparse()

            if key in items:
                words, old_vec, colors = items[key]
                color_idx[key] += 1
                colors = [
                    color_idx[key] if v != 0 else old_color
                    for old_color, v in zip(colors, vec)
                ]
                vec = np.max([old_vec, vec], axis=0)
                items[key] = (words, vec, colors)
            else:
                color_idx[key] = 0
                items[key] = (cluster.words, vec, [0] * cluster.text_length)

        self.plot(list(items.values()))

    def plot_word_vecs(self):
        items = []
        for vec in self.topics.word_vecs:
            items.append((vec.words, vec.as_sparse(), vec.text_length * [1]))
        self.plot(items)

    def plot_condensed(self):
        items = []
        for vec in self.topics.condensed:
            items.append((vec.words, vec.as_sparse(), vec.text_length * [1]))
        self.plot(items)

    def plot(self, items=[], bubble_size=25):
        n_rows = len(items)
        _, axs = plt.subplots(nrows=n_rows, sharex=True, figsize=(15, n_rows))
        x = np.arange(len(self.topics.captions))
        y = [0] * len(self.topics.captions)

        for i, ax in enumerate(axs):
            ax.spines["left"].set_visible(False)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["bottom"].set_visible(False)
            ax.get_yaxis().set_visible(False)

            words, indices, colors = items[i]
            bubbles = [
                bubble_size if data_point > 0 else 0
                for i, data_point in enumerate(indices)
            ]

            ax.title.set_text(", ".join(words[:10]))
            ax.scatter(x, y, c=colors, s=bubbles, cmap="Dark2")

        plt.show()


def is_partially_contained(line_a, line_b, amount):
    """
    line_x: tuple where 0th element is start, 1th element is end
    amount: amount line b should overlap with line a (ratio between 0 and 1)
    """
    a_length = line_a[1] - line_a[0]
    dist_start = np.absolute(line_a[0] - line_b[0])
    dist_end = np.absolute(line_a[1] - line_b[1])
    return dist_start + dist_end < amount * a_length


def is_fully_contained(line_a, line_b):
    return line_b[0] >= line_a[0] and line_b[1] <= line_a[1]


### Examples
#    0   --------
#    0 --------
assert True == is_partially_contained((2, 10), (0, 8), 0.75)
#    0 ----------
#    0    --------
assert True == is_partially_contained((0, 10), (3, 11), 0.75)
#    0 ----------
#    0      -------
assert True == is_partially_contained((0, 10), (5, 12), 0.75)
#    0 ------------
#    0    -------------
assert True == is_partially_contained((0, 12), (3, 16), 0.75)
#    0  ----------
#    0 --------------
assert True == is_partially_contained((1, 10), (0, 14), 0.75)
#    0 --------
#    0 --------------
assert False == is_partially_contained((0, 8), (0, 14), 0.75)
assert True == is_partially_contained((138, 413), (298, 452), 0.75)
