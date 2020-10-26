"""
Format the Youtube API responses into Episode objects
"""

import json
from typing import List
from dataclasses import dataclass
import os
import re


@dataclass
class Comment:
    likes: int
    text_original: str
    # text_display: str
    # published_at: str
    # author_name: str
    # author_channel_id: str


@dataclass
class Caption:
    text: str
    start: str
    duration: str


class NoCaptionsException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Episode:
    video_id: str
    channel_id: str
    title: str
    description: str
    number: str  # Episode number, JRE specific
    published_at: str
    comments: List[Comment] = None
    captions: List[Caption] = None

    def __init__(self):
        pass

    @property
    def text(self):
        """
        Returns:
            str: All text from YT generated captions
        """
        # TODO Ensure captions are sorted
        if not self.captions:
            raise NoCaptionsException("No captions")
        return " ".join([c.text for c in self.captions])

    def __repr__(self):
        return f"[{self.video_id}] {self.title}"


class EpisodeFactory:
    def __init__(self, folder_name):
        self.folder_name = folder_name
        self.folder = os.path.join(os.path.curdir, self.folder_name)

    def get_json(self, filename: str):
        file = open(os.path.join(self.folder, filename), "r")
        return json.loads(file.read()), file

    def create_episodes(self) -> List[Episode]:
        """Generates Episode objects from JSON"""
        episodes: List[Episode] = []

        ### Build basic episode objects
        upload_json, upload_file = self.get_json("uploads.json")
        for upload in upload_json:
            episode = Episode()
            episode.video_id = upload["contentDetails"]["videoId"]
            episode.channel_id = upload["snippet"]["channelId"]
            episode.published_at = upload["snippet"]["publishedAt"]
            episode.title = upload["snippet"]["title"]
            episode.description = upload["snippet"]["description"]

            # TODO This could be an MMA show
            number = re.findall(r"#\d\d?\d?\d?", episode.title)
            if len(number) > 0:
                episode.number = int(number[0].split("#")[1])
            # else:
            #     print("Could not get number for episode", episode.title)

            episodes.append(episode)
        upload_file.close()

        ### Get captions for each episode
        captions_json, captions_file = self.get_json("captions.json")
        for video_id, captions in captions_json.items():
            episode = [e for e in episodes if e.video_id == video_id][0]
            episode.captions = []
            for c in captions:
                caption = Caption(
                    text=c["text"], start=c["start"], duration=c["duration"]
                )
                episode.captions.append(caption)
        captions_file.close()

        ### Get comments for each episode
        print("loading comments...")
        comments_json, comments_file = self.get_json("comments.json")
        print("\topened file...")
        for video_id, comments in comments_json.items():
            episode = [e for e in episodes if e.video_id == video_id][0]
            episode.comments = []
            for c in comments:
                if "topLevelComment" in c["snippet"]:
                    c = c["snippet"]["topLevelComment"]["snippet"]
                else:
                    c = c["snippet"]
                if c["likeCount"] < 5:
                    continue
                comment = Comment(text_original=c["textOriginal"], likes=c["likeCount"])
                episode.comments.append(comment)
        comments_file.close()

        # stats_json

        return episodes
