import os
from typing import Literal

import arxiv
import openai
import tiktoken
from pypdf import PdfReader


class Summarizer:
    result: arxiv.Result
    lang: Literal["ja", "en"]
    content: Literal[
        "arxiv_summary",  # use arxiv's summary text and "gpt-3.5-turbo", this results cheaper than "pdf".
        "pdf",  # use whole contents of the pdf and "gpt-3.5-turbo-16k", this results more expensive but maybe better result.
    ]

    def __init__(
        self, result: arxiv.Result, lang="ja", content="arxiv_summary"
    ) -> None:
        self.result = result
        self.lang = lang
        self.content = content

    @property
    def system_prompt(self) -> str:
        if self.lang == "ja":
            return """List three key points of the given paper in bullet points, and at last, translate them into Japanese. Japanese translation is important.
In this task, please keep following rules:
- Remove general expressions such as "This paper ...", "In this method ..." and increase the density of information.
- Only use the contents of the paper in the summary, not the reference papar titles.
"""
        elif self.lang == "en":
            return """List three key points of the given paper in bullet points.
In this task, please keep following rules:
- Remove general expressions such as "This paper ...", "In this method ..." and increase the density of information.
- Only use the contents of the paper in the summary, not the reference papar titles.
"""
        else:
            raise NotImplementedError

    def summarize(self) -> str:
        if self.content == "pdf":
            return self.__summarize_pdf()
        elif self.content == "arxiv_summary":
            return self.__summarize_arxiv_summary()
        else:
            raise NotImplementedError

    def __summarize_pdf(self) -> str:
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

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.25,
        )
        return response["choices"][0]["message"]["content"]

    def __summarize_arxiv_summary(self) -> str:
        text = f"title: {self.result.title}\nbody: {self.result.summary}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.25,
        )
        return response["choices"][0]["message"]["content"]
