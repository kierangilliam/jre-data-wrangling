import numpy as np
import cv2
from matplotlib import pyplot as plt
import pandas as pd
import imutils


def get_frames(
    cap, resize_to_width=None, window=1000, grayscale=False, skip=None, start=0
):
    "`skip`: how many to skip between additions"
    frames = []
    no_more_frames = False

    cap.set(cv2.CAP_PROP_POS_FRAMES, start)

    while len(frames) < window:
        ret, frame = cap.read()

        if not ret:
            return frames, True

        if resize_to_width:
            frame = imutils.resize(frame, width=resize_to_width)

        if grayscale:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        frames.append(frame)

        # TODO probably can do another cap.set(frame)
        if skip:
            for _ in range(skip):
                cap.read()

    return frames, False


def get_averages(frames):
    averages = []
    for i, frame in enumerate(frames[1:]):
        avg = np.mean([frame, frames[i]])
        averages.append(avg)
    return np.array(averages)


# Loop over entire video and compute averages for all of the frames
def averages_for_video(
    filename, grayscale=False, fps_divis=None, scale=None, window=2500
):
    """
    fps_divis: terrible name but how many divisions of fps you want for averages. if fps is 30 and fps_divis is 2,
    grab 15 frames per. Larger the divis, the better the averaging will be for quick moves between frames, but the longer
    it will take
    window: how many frames to process at one time (batch, only relates to how much RAM
    you're willing to use)
    """
    averages = []
    n = 0
    done = False

    cap = cv2.VideoCapture(filename)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    skip = None if fps_divis is None else round(fps / fps_divis)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) * scale) if scale else None

    while not done:
        frames, done = get_frames(
            cap,
            window=window,
            skip=skip,
            start=n * window,
            grayscale=grayscale,
            resize_to_width=width,
        )

        averages.extend(get_averages(frames))

        frames = None
        n += 1

        # print(f"{round(n * window / total_frames, 2)}% ({filename[-40:-16]})")

    cap.release()

    return np.array(averages), total_frames


# from sklearn.cluster import MeanShift, estimate_bandwidth, KMeans, DBSCAN
# from sklearn.neighbors.kde import KernelDensity
# from scipy.signal import argrelextrema


# def kde_cluster(Xdf, kernel="gaussian", bandwidth=10, plot=False):
#     """
#     Uses KDE to create clusters out of word vecs
#     """
#     X = np.array(Xdf["x"])
#     X = X.reshape(-1, 1)

#     # TODO There is probably bias at the boundaries, should mirror X
#     kde = KernelDensity(kernel=kernel, bandwidth=bandwidth).fit(X)
#     s = np.linspace(0, np.max(X) * 1.5)
#     e = kde.score_samples(s.reshape(-1, 1))

#     # Reshape back to a 1 by N array
#     X = X.reshape(1, -1)

#     minima = argrelextrema(e, np.less)[0]
#     # Use the linspace to convert back into word indexes
#     minima = [s[m] for m in minima]
#     # (0, minima 1), (minima 1, minima 2), ... (minima n-1, minima n), (minima n, end)
#     minima_pairs = list(zip(np.insert(minima, 0, 0), np.append(minima, s[-1])))

#     clusters = [
#         np.unique(X[np.logical_and(X >= m1, X < m2)]) for m1, m2 in minima_pairs
#     ]

#     if plot:
#         plt.plot(s, e)
#         plt.show()
#         print(f"Number of clusters: {len(clusters)}")
#         for c in clusters:
#             print("\t", len(c), np.unique([int(x) for x in c]))

#     return clusters


# # Store frame numbers in the clusters instead of the average of the last frame
# def frame_idxs_clusters(aavg_clusters, df):
#     df_2 = df_avg.copy()
#     df_2["cluster"] = np.full_like((len(averages)), -1)

#     # clusters = []
#     for i, c in enumerate(avg_clusters):
#         # clusters.append([])
#         for j, frame in enumerate(frames[:-1]):
#             if normal_averages[j] >= np.min(c) and normal_averages[j] <= np.max(c):
#                 clusters[i].append(j)
#                 df_2["cluster"][j] = i
#                 continue

#     return df_2
