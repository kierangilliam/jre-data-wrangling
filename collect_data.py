# -*- coding: utf-8 -*-

# Sample Python code for youtube.channels.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os

import re
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
import googleapiclient.errors
from pprint import pprint
import json
from youtube_transcript_api import YouTubeTranscriptApi
from tqdm import tqdm
from pytube import YouTube


API_KEY = "AIzaSyDVxHE-OCeVAFC2AUx8GWo63P5QtHPvngQ"

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"

    youtube = build(api_service_name, api_version, developerKey=API_KEY)

    # request = youtube.videos().list(
    #     part="contentDetails,fileDetails,id,liveStreamingDetails,localizations,player,processingDetails,recordingDetails,snippet,statistics,status,suggestions,topicDetails",
    # )
    # request = youtube.channels().list(
    #     # part="snippet,contentDetails,statistics,uploads",
    #     part="contentDetails",
    #     forUsername="PowerfulJRE"
    # )

    def get_uploads(upload_id):
        page_token = None
        items = []
        total_results = 0

        while True:
            print(f"{len(items)}/{total_results} -> {page_token}")

            request = youtube.playlistItems().list(
                part="contentDetails,id,snippet,status",
                playlistId=upload_id,
                pageToken=page_token,
                maxResults=50,
            )
            response = request.execute()
            items.extend(response["items"])

            total_results = response["pageInfo"]["totalResults"]

            if "nextPageToken" in response:
                page_token = response["nextPageToken"]
            else:
                break

        return items

    # uploads = get_uploads("UUzQUP1qoWDoEbmsQxvdjxgQ")
    # with open("uploads.json", "w") as f:
    #     f.write(json.dumps(uploads))

    # captions = {}
    # failed_to_get_captions = []
    # with open("uploads.json", "r") as f:
    #     uploads = json.loads(f.read())

    #     for i, upload in enumerate(uploads):
    #         print(f"{i}/{len(uploads)}")
    #         id = upload["contentDetails"]["videoId"]

    #         try:
    #             caption = YouTubeTranscriptApi.get_transcript(id)
    #             captions[id] = caption
    #         except:
    #             failed_to_get_captions.append(id)

    #         # save progress
    #         if i % 10 == 0:
    #             with open("captions.json", "w") as f:
    #                 f.write(json.dumps(captions))

    # with open("captions.json", "w") as f:
    #     f.write(json.dumps(captions))

    # with open("failed_to_get_captions.json") as f:
    #     f.write(json.dumps(failed_to_get_captions))

    ########################################
    # Create a combined file with all of the
    # caption text without timestamps
    # with open("captions.json", "r") as f:
    #     captions = json.loads(f.read())

    #     raw_text = ""
    #     for key, caption in captions.items():
    #         raw_text += "\n".join([c["text"] for c in caption])

    #     with open("raw_text.txt", "w") as ff:
    #         ff.write(raw_text)

    def get_comments(videoId, max=1500):
        page_token = None
        items = []
        # print(videoId)

        while True and len(items) < max:
            # print(f"\t{len(items)}/{max}")
            request = youtube.commentThreads().list(
                part="id,snippet",
                videoId=videoId,
                pageToken=page_token,
                maxResults=500,
                order="relevance",
            )
            response = request.execute()
            items.extend(response["items"])

            if "nextPageToken" in response:
                page_token = response["nextPageToken"]
            else:
                break

        return items

    #######################################
    # Get comments and statistics for each video
    UPLOADS = "data/jre/uploads.json"
    COMMENTS = "data/jre/comments.json"
    # with open(UPLOADS, "r") as f:
    #     uploads = json.loads(f.read())

    #     # likeCount, textDisplay, textOriginal, publishedAt
    #     # authorDisplayName, authorChannelId
    #     i = 0
    #     comment_threads = {}
    #     with open(COMMENTS, "r") as f:
    #         comment_threads = json.load(f)

    #     for upload in tqdm.tqdm(uploads):
    #         videoId = upload["snippet"]["resourceId"]["videoId"]

    #         if videoId not in comment_threads:
    #             comments = get_comments(videoId)
    #             comment_threads[videoId] = comments
    #             print(videoId, len(comments))
    #         else:
    #             print("Already saved thread for", videoId)

    #         i += 1
    #         # save progress
    #         if i % 25 == 0:
    #             with open(COMMENTS, "w") as f:
    #                 f.write(json.dumps(comment_threads))

    #     with open(COMMENTS, "w") as f:
    #         f.write(json.dumps(comment_threads))
    # audio_file = lambda id: f"data/jre/audio/{id}"
    # with open(UPLOADS, "r") as f:
    #     uploads = json.loads(f.read())

    #     for upload in tqdm(uploads):
    #         id = upload["contentDetails"]["videoId"]
    #         yt = None
    #         if os.path.exists(audio_file(id)):
    #             print("File exists", id, "skipping...")
    #             continue

    #         try:
    #             yt = YouTube(f"https://www.youtube.com/watch?v={id}")
    #         except Exception as e:
    #             print("Could not load api", id, str(e))
    #             continue

    #         audio_streams = yt.streams.filter(only_audio=True)

    #         if len(audio_streams) == 0:
    #             print("No audio streams available for", id)
    #             continue

    #         mp4_streams = [s for s in audio_streams if s.mime_type == "audio/mp4"]
    #         stream = audio_streams[0] if len(mp4_streams) == 0 else mp4_streams[0]

    #         print(f"Downloading [{id}] {stream.mime_type} {stream.abr}")
    #         stream.download(audio_file(id))
    #         print("\t... Done")

    # def get_timestamps(c):
    #     timestamp = r"(\d?\d?:)?\d?\d?:\d{2}"

    #     if "topLevelComment" in c["snippet"]:
    #         snippet = c["snippet"]["topLevelComment"]["snippet"]

    #         if re.search(timestamp, snippet["textOriginal"]) is None:
    #             return None
    #         return snippet["likeCount"], snippet["textOriginal"]
    #     elif re.search(timestamp, c["snippet"]["textOriginal"]) is not None:
    #         return c["snippet"]["likeCount"], c["snippet"]["textOriginal"]


if __name__ == "__main__":
    main()