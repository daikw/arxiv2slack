# see also: https://platform.openai.com/docs/models/gpt-3-5

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import arxiv
import openai
import random

import tiktoken
from pypdf import PdfReader

SLACK_API_TOKEN = os.environ["SLACK_API_TOKEN"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]
ARXIV_QUERY = os.environ["ARXIV_QUERY"]


def summarize_pdf(result: arxiv.Result) -> str:
    if not os.path.isdir("./tmp"):
        os.mkdir("./tmp")
    filepath = result.download_pdf("./tmp")

    pdf = PdfReader(filepath)
    text = ""
    for page in pdf.pages:
        text += page.extract_text()

    # if token count exceeds, truncate text
    enc = tiktoken.get_encoding("gpt2")
    tokens = enc.encode(text)
    if len(tokens) > 16384:
        text = text[:16384]

    system = """与えられた論文の要点を3つ挙げ、日本語で箇条書きにまとめてください。ただし、「この論文では」などの一般的な冒頭の表現は取り除き、情報の密度を高めてください。"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": text},
        ],
        temperature=0.25,
    )
    return response["choices"][0]["message"]["content"]


def summarize(result: arxiv.Result) -> str:
    system = """与えられた論文の要点を3つ挙げ、日本語で箇条書きにまとめてください。ただし、「この論文では」などの一般的な冒頭の表現は取り除き、情報の密度を高めてください。"""
    text = f"title: {result.title}\nbody: {result.summary}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": text},
        ],
        temperature=0.25,
    )
    return response["choices"][0]["message"]["content"]


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

    # Sample papers
    results = random.sample(result_list, k=3)

    # Post to Slack
    for i, result in enumerate(results):
        message = f"""*今日の論文ピックアップ #{i + 1}*
*Link*: {result.entry_id}
*Title*: {result.title}
*PublishedAt*: {result.published.strftime('%Y-%m-%d %H:%M:%S')}
---
{summarize_pdf(result)}
"""
        try:
            response = client.chat_postMessage(
                channel=SLACK_CHANNEL,
                mrkdwn=True,
                text=message,
                unfurl_links=False,
            )
            print(f"Message posted: {response['ts']}")  # ts stands for `timestamp`
        except SlackApiError as e:
            print(f"Error posting message: {e}")


if __name__ == "__main__":
    client = WebClient(token=SLACK_API_TOKEN)
    main(client)
