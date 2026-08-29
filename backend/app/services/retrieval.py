"""
Information Retrieval module.

Implements a real TF-IDF + cosine similarity retrieval pipeline over a local
corpus of documents. Documents are split into passages (paragraph / sentence
groups) so that retrieval granularity is closer to "relevant passage" rather
than whole-document.
"""
import os
import re
from dataclasses import dataclass
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Passage:
    doc_id: str
    doc_title: str
    text: str


def _split_sentences(text: str) -> List[str]:
    # Lightweight sentence splitter (avoids extra NLTK downloads at runtime).
    text = text.strip().replace("\n", " ")
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


class TfidfRetriever:
    """
    Loads all .txt files from a directory, splits each into passages
    (here: whole document is also usable as one passage, but we additionally
    index individual sentences so we can point to fine-grained evidence),
    builds a TF-IDF index, and supports ranked retrieval by cosine similarity.
    """

    def __init__(self, corpus_dir: str):
        self.corpus_dir = corpus_dir
        self.passages: List[Passage] = []
        self.sentences: List[Passage] = []
        self._load_corpus()
        self._build_index()

    def _load_corpus(self):
        for fname in sorted(os.listdir(self.corpus_dir)):
            if not fname.endswith(".txt"):
                continue
            path = os.path.join(self.corpus_dir, fname)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read().strip()
            title = fname.replace(".txt", "").replace("_", " ").title()
            self.passages.append(Passage(doc_id=fname, doc_title=title, text=text))
            for sent in _split_sentences(text):
                self.sentences.append(Passage(doc_id=fname, doc_title=title, text=sent))

    def _build_index(self):
        # Passage-level index (document granularity)
        self.passage_vectorizer = TfidfVectorizer(stop_words="english")
        self.passage_matrix = self.passage_vectorizer.fit_transform(
            [p.text for p in self.passages]
        )
        # Sentence-level index (fine-grained evidence / answer sentence selection)
        self.sentence_vectorizer = TfidfVectorizer(stop_words="english")
        self.sentence_matrix = self.sentence_vectorizer.fit_transform(
            [s.text for s in self.sentences]
        )

    def retrieve_passages(self, query: str, top_k: int = 3):
        """Rank whole documents/passages by cosine similarity to the query."""
        query_vec = self.passage_vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.passage_matrix)[0]
        ranked_idx = scores.argsort()[::-1][:top_k]
        results = []
        for idx in ranked_idx:
            results.append({
                "doc_id": self.passages[idx].doc_id,
                "doc_title": self.passages[idx].doc_title,
                "text": self.passages[idx].text,
                "score": round(float(scores[idx]), 4),
            })
        return results

    def retrieve_sentences(self, query: str, top_k: int = 5, doc_id: str = None):
        """Rank individual sentences by cosine similarity, optionally restricted to one doc."""
        query_vec = self.sentence_vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.sentence_matrix)[0]
        indices = list(range(len(self.sentences)))
        if doc_id:
            indices = [i for i in indices if self.sentences[i].doc_id == doc_id]
        indices.sort(key=lambda i: scores[i], reverse=True)
        indices = indices[:top_k]
        results = []
        for idx in indices:
            results.append({
                "doc_id": self.sentences[idx].doc_id,
                "text": self.sentences[idx].text,
                "score": round(float(scores[idx]), 4),
            })
        return results

    def list_documents(self):
        return [{"doc_id": p.doc_id, "title": p.doc_title, "preview": p.text[:160] + "..."} for p in self.passages]
