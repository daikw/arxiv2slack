import time
import random
from typing import Literal

import arxiv


class ArxivSampler:
    query: str
    strategy: Literal[
        "random",  # default, random sampling from 100 top-relevant results
        "latest",  # latest k papers
        "dayly",  # random sampling from all papers published in 24 hours
        "weekly",  # random sampling from all papers published in 24 * 7 hours
    ]
    results: list[arxiv.Result]

    def __init__(self, query: str, strategy: str = "random") -> None:
        self.query = query
        self.strategy = strategy

    def sample(self, k: int = 3) -> list[arxiv.Result]:
        """Sampling papers from arXiv search results.

        Args:
            k (int, optional): Number of papers to sample. Defaults to 3.

        Returns:
            list[arxiv.Result]: List of sampled papers.
        """

        if self.strategy == "random":
            search = arxiv.Search(
                query=self.query,
                max_results=100,
                sort_by=arxiv.SortCriterion.Relevance,
            )
            tmp: list[arxiv.Result] = []
            for result in search.results():
                tmp.append(result)

            if len(tmp) < k:
                return tmp
            else:
                return random.sample(tmp, k=k)

        elif self.strategy == "latest":
            search = arxiv.Search(
                query=self.query,
                max_results=3,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending,
            )
            tmp: list[arxiv.Result] = []
            for result in search.results():
                tmp.append(result)
                if len(tmp) >= 3:
                    break  # defensive break
            return tmp

        elif self.strategy == "daily":
            search = arxiv.Search(
                query=self.query,
                max_results=100,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending,
            )
            tmp: list[arxiv.Result] = []
            now = time.time()
            for result in search.results():
                delta = now - result.published.date().timestamp()
                if delta < 24 * 60 * 60:
                    tmp.append(result)
                else:
                    break

            if len(tmp) < k:
                return tmp
            else:
                return random.sample(tmp, k=k)

        elif self.strategy == "weekly":
            search = arxiv.Search(
                query=self.query,
                max_results=100,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending,
            )
            tmp: list[arxiv.Result] = []
            now = time.time()
            for result in search.results():
                delta = now - result.published.timestamp()
                if delta < 24 * 60 * 60 * 7:
                    tmp.append(result)
                else:
                    break

            if len(tmp) < k:
                return tmp
            else:
                return random.sample(tmp, k=k)
