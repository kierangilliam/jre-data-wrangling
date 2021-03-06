import multiprocessing
import sys

from src.lib.VideoAverages import averages_for_video
import numpy as np
import time
import glob
import os
from random import shuffle

PROCS = 2
ID = "flagrant2"
videos_location = f"/mnt/volume_sfo2_01/{ID}/"
SCALE = 0.5
GRAYSCALE = False
avg_cache = (
    f"./data/{ID}/averages_scale.{SCALE*100}_"
    + ("grayscale" if GRAYSCALE else "color")
    + "/"
)


if not os.path.exists(avg_cache):
    print("Making directory to store averages...", avg_cache)
    os.makedirs(avg_cache)

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
                flush=True,
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
    shuffle(files)
    
    print(len(files))
    print(f"Running on {PROCS} processes")

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
