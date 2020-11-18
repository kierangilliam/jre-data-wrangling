import multiprocessing
import sys

from src.lib.VideoSegment import averages_for_video
import numpy as np
import time
import glob
import os


avg_cache = "./data/jre/averages_fps_divis_5/"
avgfn = lambda x: avg_cache + x.split("../videos/")[1].split(".mp4")[0]

def process_files(filenames):
    print(len(filenames))

    def process():
        sys.stdout = open("avgs_" + str(os.getpid()) + ".out", "a")
        sys.stderr = open(str(os.getpid()) + "_error.out", "a")

        for i, fn in enumerate(filenames):
            print(
                f"{round(i/len(filenames),3)*100} - [{i}/{len(filenames)}]",
                fn,
                flush=True,
            )
            averages, total_frames = averages_for_video(fn, fps_divis=5)
            np.save(avgfn(fn), [averages, total_frames])

    return process


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


if __name__ == "__main__":
    PROCS = 8

    files = list(glob.glob("../videos/*.mp4"))
    files = [f for f in files if not os.path.exists(avgfn(f) + ".npy")]
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
