# CUDA_VISIBLE_DEVICES= python3 diarization.py

import multiprocessing
import pydub
import sys
import time
import glob
import os
from pyannote.core import Segment
import torch
import pickle


pipeline = torch.hub.load('pyannote/pyannote-audio', 'dia', device='cpu')
CACHE = "./data/jre/diarization/"


def convert_to_wav(mp4):
    def W(x): return "./" + x.split("../videos/")[1].split('.mp4')[0] + ".wav"
    print(mp4, W(mp4))
    sound = pydub.AudioSegment.from_file(mp4, format="mp4")
    print("EXPORT")
    #sound.export(W(mp4), format="wav")
    sound.export("./JOE.wav", format="wav")
    sound = None
    return W(mp4)


def process_files(filenames):
    print(len(filenames))
    N = lambda x: CACHE + x.split("../videos/")[1].split('.mp4')[0] + ".pkl"
    filenames = [f for f in filenames if not os.path.exists(N(f))]

    torch.set_num_threads(multiprocessing.cpu_count())

   
    def process():
    #    sys.stdout = open("DIARIZATION_" + str(os.getpid()) + ".out", "a")
    #    sys.stderr = open(str(os.getpid()) + "_error.out", "a")

        for i, fn in enumerate(filenames):
            print(f"{round(i/len(filenames)*100,3)} - [{i}/{len(filenames)}]", fn, flush=True)

            #wav = convert_to_wav(fn)
            wav = "test.wav"
            print(f"\tDiarization {wav}...", flush=True)
            diarization = pipeline({'audio': wav})
            print(f"\tDone...", flush=True)

            #os.system(f"rm '{wav}'")

            #with open(N(fn), "wb") as f:
             #   f.write(pickle.dump(diarization))
            return

    return process


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


if __name__ == "__main__":
    PROCS = 1

    files = list(glob.glob("../videos/*.mp4"))
    files = list(chunks(files, len(files) // PROCS))
    starttime = time.time()
    processes = []

    for i in range(PROCS):
        p = multiprocessing.Process(target=process_files(files[i]))
        processes.append(p)
        p.start()

    for process in processes:
        process.join()

