from tqdm import tqdm
import time
import json
import youtube_dl
import pickle
from glob import glob
from lib.Episode import Episode, EpisodeFactory
import os
import shutil

ID = "lex"
BASE = f"../data/{ID}"
VIDEOS_LOCATION = f"../../videos/{ID}/"
CACHE = f"./{ID}-episodes.pickle"
CREATE_CACHE = False
ONLY_DOWNLOAD_MAIN = False

if CREATE_CACHE == True:
    print(f"Generating new pickle {CACHE}...")

    factory = EpisodeFactory(BASE)
    episodes = factory.create_episodes(skip_comments=True)

    with open(CACHE, "wb") as f:
        pickle.dump(episodes, f)

with open(CACHE, "rb") as f:
    episodes = pickle.load(f)

eps = [e for e in episodes if not ONLY_DOWNLOAD_MAIN or (ONLY_DOWNLOAD_MAIN and e.is_main_episode)]
print("Total downloadable episodes", len(eps))

video_files = list(glob(VIDEOS_LOCATION + "*.mp4"))
video_files_ids = [v[-15:-4] for v in video_files]
downloaded = [e for e in eps if e.video_id in video_files_ids] or []

# sort to give priority to newer episodes first
missing_videos = sorted(
    list(set(eps) - set(downloaded)),
    key=lambda ep: ep.published_at,
    reverse=True,
)

print("Total missing downloadable videos", len(missing_videos))

ydl = youtube_dl.YoutubeDL(
    {
        # MP4 at 360p
        "format": "18",
        # "cookiefile": "./youtube-dl-cookies.txt"
    }
)

downloaded = 0
with ydl:
    for ep in tqdm(missing_videos):
        video = f"http://www.youtube.com/watch?v={ep.video_id}"

        try:
            result = ydl.download([video])
            downloaded += 1

            # Couldn't get option "outtml" to work, manually move instead
            try:
                file = list(glob(f"./*{ep.video_id}.mp4"))[0]
                shutil.move(f"./{file}", VIDEOS_LOCATION + f"{ep.video_id}.mp4")
            except Exception as e:
                print("Could not move", ep, e)

        except Exception as e:
            print("could not download", ep.title)

        time.sleep(15)

print("Downloaded", downloaded, "videos")
