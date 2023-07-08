# see also: https://platform.openai.com/docs/models/gpt-3-5

import os
import random

import arxiv
from slack_sdk import WebClient

from summarize import Summarizer

SLACK_API_TOKEN = os.environ["SLACK_API_TOKEN"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]
ARXIV_QUERY = os.environ["ARXIV_QUERY"]

SUMMARIZE_LANGUAGE = os.environ.get("SUMMARIZE_LANGUAGE", "ja")
SUMMARIZE_CONTENT = os.environ.get("SUMMARIZE_CONTENT", "arxiv_summary")


def main(client: WebClient):
    search = arxiv.Search(
        query=ARXIV_QUERY,
        max_results=100,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )
    result_list: list[arxiv.Result] = []
    for result in search.results():
        result_list.append(result)

    if len(result_list) == 0:
        client.chat_postMessage(
            channel=SLACK_CHANNEL,
            text="今日の論文ピックアップはありませんでした。",
        )
    elif len(result_list) < 3:
        results = result_list
    else:
        # Sampling papers
        results = random.sample(result_list, k=3)

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
