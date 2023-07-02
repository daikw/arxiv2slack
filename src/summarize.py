import os
import arxiv
import openai

import tiktoken
from pypdf import PdfReader


class Summarizer:
    result: arxiv.Result

    def __init__(self, result: arxiv.Result) -> None:
        self.result = result

    def summarize_pdf(self) -> str:
        if not os.path.isdir("./tmp"):
            os.mkdir("./tmp")
        filepath = self.result.download_pdf("./tmp")

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

    def summarize(self) -> str:
        system = """与えられた論文の要点を3つ挙げ、日本語で箇条書きにまとめてください。ただし、「この論文では」などの一般的な冒頭の表現は取り除き、情報の密度を高めてください。"""
        text = f"title: {self.result.title}\nbody: {self.result.summary}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": text},
            ],
            temperature=0.25,
        )
        return response["choices"][0]["message"]["content"]
