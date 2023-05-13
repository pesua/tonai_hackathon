import requests, cohere, json
from cohere.responses.classify import Example


# Keep in mind that currently Cohere supports summary for transcripts size up to 100 000 symbols. Everything above that limit may be a source of bugs.

def summarizeHealthcare(pathToFile):
    # Setup
    print("Starting up analysis.")
    co = cohere.Client('STYMNTiot9LWDLeJbEkXyDVYxYg1IIaavlTUeDoz')

    ## Getting summary here
    with open(pathToFile, 'r') as file:
        content = file.read()
        if len(content) > 100000:
            content_array = [content[i:i + 100000] for i in range(0, len(content), 100000)]
        else:
            content_array = [content]

    summary_array = []

    while len(content_array) > 0:
        text = content_array.pop()
        responce = co.summarize(text=text, length="long")
        summary_array.append(responce.summary);

    with open('tags.json', 'r') as f:
        data = json.load(f)

    examples = [Example(d['definition'], d['tag']) for d in data]

    ## Getting tags
    with open(pathToFile, 'r') as file:
        content = file.read()
        if len(content) > 100000:
            content_array = [content[i:i + 100000] for i in range(0, len(content), 100000)]
        else:
            content_array = [content]

    response_tags = co.classify(inputs=content_array, examples=examples)

    ## Setting up a result
    with open(pathToFile, 'r') as file:
        rawText = file.read()
        tags = set([])
        summary = ""
        for tag in response_tags:
            tags.add(tag.prediction)
        for summary_element in summary_array:
            summary = summary + summary_element + "\n"

    result = {"rawText": rawText,
              "tags": list(tags),
              "summary": summary}

    return json.dumps(result)
