import multiprocessing
from src.lib.VideoSegment import averages_for_video
import numpy as np
import time
import glob
import os


def process_files(filenames):
    avg_cache = "./data/jre/videos/averages"
    avgfn = lambda x: avg_cache + x + f".average"

    def process():
        for fn in filenames:
            if os.path(avgfn(fn)).exists:
                print(fn, "exists, skipping...")
                continue

            averages, total_frames = averages_for_video(fn)
            np.save(avgfn(fn), [averages, total_frames])

    return process


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


if __name__ == "__main__":
    PROCS = 4

    files = list(glob.glob("../videos/*.mp4"))
    files = list(chunks(files, PROCS))
    starttime = time.time()
    processes = []

    for i in range(PROCS):
        p = multiprocessing.Process(target=process_files(files[i]))
        processes.append(p)
        p.start()

    for process in processes:
        process.join()

    print("That took {} seconds".format(time.time() - starttime))
