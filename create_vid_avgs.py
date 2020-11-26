import multiprocessing
import sys

from src.lib.VideoSegment import averages_for_video
import numpy as np
import time
import glob
import os

PROCS = 3
videos_location = "/Volumes/JRE/jre-bucket/jre/videos/"
SCALE = 0.25
GRAYSCALE = False
# TODO COMPARE SPEED WITH/WITHOUT GRAYSCALE
# FPS_DIVIS = 15
avg_cache = (
    f"./data/jre/averages_scale.{SCALE*100}_"
    + ("grayscale" if GRAYSCALE else "color")
    + "/"
)
avgfn = lambda x: avg_cache + x.split(videos_location)[1].split(".mp4")[0]


def process_files(filenames):
    print(len(filenames))

    def process():
        # sys.stdout = open("avgs_" + str(os.getpid()) + ".out", "a")
        # sys.stderr = open(str(os.getpid()) + "_error.out", "a")

        for i, fn in enumerate(filenames):
            print(
                f"{round(i/len(filenames),3)*100} - [{i}/{len(filenames)}]",
                fn,
                # flush=True,
            )
            averages, total_frames = averages_for_video(
                fn, scale=SCALE, grayscale=GRAYSCALE
            )
            np.save(avgfn(fn), [averages, total_frames])

    return process


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


if __name__ == "__main__":
    if not os.path.exists(avg_cache):
        print("Making directory", avg_cache)
        os.makedirs(avg_cache)

    print("SCALE", SCALE)
    print("GRAYSCALE", GRAYSCALE)

    files = list(glob.glob(videos_location + "*.mp4"))
    files = [f for f in files if not os.path.exists(avgfn(f) + ".npy")]

    files = [
        f
        for f in files
        if "#1539 - Jenny Kleeman" in f
        or "#1538 - Douglas Murray" in f
        or "#1536 - Edward Snowden" in f
    ]
    print(files)

    files = list(chunks(files, len(files) // PROCS))
    starttime = time.time()
    processes = []

    for i in range(PROCS):
        p = multiprocessing.Process(target=process_files(files[i]))
        processes.append(p)
        p.start()

    for process in processes:
        process.join()

    print("That took {} seconds".format(time.time() - starttime))
