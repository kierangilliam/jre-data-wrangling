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

    cap.release()

    return np.array(averages), total_frames
