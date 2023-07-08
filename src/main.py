# see also: https://platform.openai.com/docs/models/gpt-3-5

import os

from slack_sdk import WebClient

from summarizer import Summarizer
from search import ArxivSampler

SLACK_API_TOKEN = os.environ["SLACK_API_TOKEN"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]
ARXIV_QUERY = os.environ["ARXIV_QUERY"]

SUMMARIZE_LANGUAGE = os.environ.get("SUMMARIZE_LANGUAGE", "ja")
SUMMARIZE_CONTENT = os.environ.get("SUMMARIZE_CONTENT", "arxiv_summary")


def main(client: WebClient):
    results = ArxivSampler(query=ARXIV_QUERY, strategy="daily").sample(k=3)
    if len(results) == 0:
        client.chat_postMessage(
            channel=SLACK_CHANNEL,
            text="今日の論文ピックアップはありませんでした。",
        )
        return

    # Post to Slack
    for i, result in enumerate(results):
        message = f"""*今日の論文ピックアップ #{i + 1}*
*Link*: {result.entry_id}
*Title*: {result.title}
*PublishedAt*: {result.published.strftime('%Y-%m-%d %H:%M:%S')}
*FirstAuthor*: {result.authors[0].name}
---
{Summarizer(result, lang=SUMMARIZE_LANGUAGE, content=SUMMARIZE_CONTENT).summarize()}
"""
        response = client.chat_postMessage(
            channel=SLACK_CHANNEL,
            mrkdwn=True,
            text=message,
            unfurl_links=False,
        )
        print(f"Message posted: {response['ts']}")  # ts stands for `timestamp`


if __name__ == "__main__":
    client = WebClient(token=SLACK_API_TOKEN)
    try:
        main(client)
    except Exception as e:
        print(e)
