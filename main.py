from youtube_transcript_api import YouTubeTranscriptApi
import openai
from yt_dlp import YoutubeDL
import pandas as pd
import logging

import re

openai.api_key = ''
logger = logging.getLogger(__name__)


def get_transcript(video_id):
    srt = YouTubeTranscriptApi.get_transcript(video_id)
    return ' '.join([s['text'] for s in srt]).replace('\n', ' ')


def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


def extract_entries_for_url(channel_url):
    list_dict = []
    entries = ydl_get_entries(channel_url)
    # workaround if channel videos are seen as a playlist
    if "_type" in entries[0]:
        if entries[0]["_type"] == "playlist":
            entries = entries[0]["entries"]
    for entry in entries:
        if entry:
            best_format = entry["formats"][-2]["format"]
            filesize = entry["formats"][-2]["filesize"]
            timecodes = parse_timecodes(entry.get("description", ""))
            subs = ""
            # subs can be empty and get_transcript fails if it's so
            if entry["subtitles"] & entry["subtitles"]["en"]:
                subs = get_transcript(entry.get("id", ""))

            list_dict.append(
                {
                    "author": entry.get("uploader", ""),
                    "channel_url": entry.get("uploader_url", ""),
                    "title": entry.get("title", ""),
                    "webpage_url": entry.get("webpage_url", ""),
                    "view_count": entry.get("view_count", ""),
                    "like_count": entry.get("like_count", ""),
                    "duration": entry.get("duration", ""),
                    "upload_date": entry.get("upload_date", ""),
                    "tags": entry.get("tags", ""),
                    "categories": entry.get("categories", ""),
                    "description": entry.get("description", ""),
                    "thumbnail": entry.get("thumbnail", ""),
                    "best_format": best_format,
                    "filesize_bytes": filesize,
                    "timecodes": timecodes,
                    "subs": subs
                }
            )
    return list_dict


def parse_timecodes(description):
    # promt for chatgpt `Help me create regexp to catch minute and seconds separated by colon`
    matched = re.findall("\\b\\d{1,2}:\\d{2}\\b", description)
    return matched


def ydl_get_entries(search_term):
    try:
        ydl_opts = {"logger": MyLogger(), "ignoreerrors": True}
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(search_term, download=False)
        return info_dict["entries"]
    except Exception as e:
        logger.error("Error with getting the youtube url for %s : %s.", search_term, e)
        return None


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


if __name__ == '__main__':
    transcript = get_transcript('XcvhERcZpWw')
    #print(transcript)

    prompt = f'Rewrite the text in quotes as a transcript of kids show, make as many jokes as possible "{transcript[:1000]}"'
    #print(get_completion(prompt))

    # huberman channel url
    entries = extract_entries_for_url('https://www.youtube.com/channel/UC2D2CMWXMOVWx7giW1n3LIg')
    export_filename = 'youtube_export_with_subs'
    df = pd.DataFrame(entries)
    df.to_csv(export_filename + ".csv", index=False, sep=";")
