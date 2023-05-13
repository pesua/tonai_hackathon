from youtube_transcript_api import YouTubeTranscriptApi
import openai

openai.api_key = ''


def get_transcript(video_id):
    srt = YouTubeTranscriptApi.get_transcript(video_id)
    return ' '.join([s['text'] for s in srt]).replace('\n', ' ')


def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


if __name__ == '__main__':
    transcript = get_transcript('XcvhERcZpWw')
    print(transcript)

    prompt = f'Rewrite the text in quotes as a transcript of kids show, make as many jokes as possible "{transcript[:1000]}"'
    print(get_completion(prompt))

