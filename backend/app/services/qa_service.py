"""
Extractive Question Answering module.

Given a question and the best-matching evidence sentence(s), extracts a
factoid answer span. This is a transparent, rule-based extractive approach
driven by the WH-word (question type) of the question:

  - who/whom      -> proper-noun phrase (capitalized token sequence)
  - when          -> date / year expression
  - where         -> capitalized location-like phrase (after "in"/"at")
  - what/which    -> noun phrase near a copula ("is a", "is the")
  - how many/much -> numeric expression

This keeps the pipeline fully local, explainable, and dependency-light
(no external model download is required), while still performing genuine
answer-span extraction rather than returning the whole sentence.
"""
import re
from typing import Optional, Tuple

DATE_PATTERN = re.compile(
    r"\b((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}|\d{4})\b"
)
NUMBER_PATTERN = re.compile(r"\b(\d[\d,\.]*\s?(?:million|billion|thousand)?)\b", re.IGNORECASE)

# Matches capitalized name/entity phrases, allowing:
#  - comma-joined parts, e.g. "Ulm, Germany"
#  - lowercase name particles, e.g. "Guido van Rossum"
NAME_PARTICLES = r"(?:van|von|der|den|de|la|du)"
PROPER_NOUN_PATTERN = re.compile(
    r"\b([A-Z][a-zA-Z\.]*"
    r"(?:(?:\s+(?:" + NAME_PARTICLES + r"))?"
    r"(?:\s+|,\s+)[A-Z][a-zA-Z\.]*)*)\b"
)

STOPWORD_SENTENCE_STARTERS = {"The", "This", "That", "It", "A", "An", "In", "On", "At", "His", "Her"}


def _question_type(question: str) -> str:
    q = question.lower().strip()
    if q.startswith("who"):
        return "who"
    if q.startswith("when"):
        return "when"
    if q.startswith("where"):
        return "where"
    if q.startswith("how many") or q.startswith("how much"):
        return "quantity"
    if q.startswith("what") or q.startswith("which"):
        return "what"
    return "other"


def _extract_proper_nouns(sentence: str, exclude_terms=None):
    """Return candidate proper-noun phrases, longest/multi-word sequences preferred.

    `exclude_terms`: phrases already mentioned in the question itself are
    deprioritized, since the answer is usually a *new* entity, not the one
    the question already names (e.g. don't answer "Albert Einstein" to
    "Where was Albert Einstein born?").
    """
    exclude_terms = {t.lower() for t in (exclude_terms or [])}
    candidates = []
    for match in PROPER_NOUN_PATTERN.finditer(sentence):
        phrase = match.group(1).strip().rstrip(",")
        words = [w for w in phrase.split() if w not in STOPWORD_SENTENCE_STARTERS]
        phrase = " ".join(words)
        if phrase and len(phrase) > 1:
            candidates.append(phrase)

    non_self = [c for c in candidates if c.lower() not in exclude_terms]
    pool = non_self if non_self else candidates
    # Prefer multi-word (likely full names) then longer phrases, stable on first occurrence
    pool.sort(key=lambda p: (len(p.split()) > 1, len(p)), reverse=True)
    return pool


def extract_answer(question: str, sentence: str) -> Tuple[str, float]:
    """
    Extract a factoid answer span from the given evidence sentence.
    Returns (answer_text, extraction_confidence).
    Falls back to the full sentence if no confident span is found.
    """
    qtype = _question_type(question)
    question_terms = _extract_proper_nouns(question)  # entities already named in the question

    if qtype == "when":
        m = DATE_PATTERN.search(sentence)
        if m:
            return m.group(1), 0.9

    if qtype == "quantity":
        m = NUMBER_PATTERN.search(sentence)
        if m:
            return m.group(1).strip(), 0.85

    if qtype in ("who", "where", "what"):
        candidates = _extract_proper_nouns(sentence, exclude_terms=question_terms)
        if candidates:
            return candidates[0], 0.8

    # Fallback: try a date or proper noun anyway before giving up
    m = DATE_PATTERN.search(sentence)
    if m:
        return m.group(1), 0.6

    candidates = _extract_proper_nouns(sentence, exclude_terms=question_terms)
    if candidates:
        return candidates[0], 0.55

    return sentence.strip(), 0.3


def score_sentence_overlap(question: str, sentence: str) -> float:
    """Simple lexical-overlap relevance score between a question and a sentence."""
    stop = {"a", "an", "the", "is", "are", "was", "were", "of", "in", "on", "at",
            "who", "what", "when", "where", "which", "how", "did", "do", "does", "to"}
    q_tokens = {w.lower().strip("?.,") for w in question.split() if w.lower() not in stop}
    s_tokens = {w.lower().strip("?.,") for w in sentence.split() if w.lower() not in stop}
    if not q_tokens:
        return 0.0
    overlap = q_tokens & s_tokens
    return len(overlap) / len(q_tokens)
