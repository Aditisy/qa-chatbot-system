"""
IR-based QA pipeline orchestration:

  Question -> Preprocessing -> Document Retrieval (TF-IDF) ->
  Passage Ranking -> Sentence Selection -> Extractive Answer -> Evidence
"""
import re
from .retrieval import TfidfRetriever
from .qa_service import extract_answer, score_sentence_overlap

# Small, explainable query-expansion map for common abbreviations found in the
# corpus. This is a standard, lightweight IR preprocessing technique (not a
# model) and keeps retrieval explainable.
ABBREVIATION_EXPANSIONS = {
    "ceo": "chief executive officer",
    "nlp": "natural language processing",
    "wwii": "world war ii",
    "ww2": "world war ii",
    "us": "united states",
}


def _expand_query(text: str) -> str:
    words = text.split()
    expanded = []
    for w in words:
        key = w.strip("?.,!").lower()
        if key in ABBREVIATION_EXPANSIONS:
            expanded.append(ABBREVIATION_EXPANSIONS[key])
        else:
            expanded.append(w)
    return " ".join(expanded)


class IRService:
    def __init__(self, corpus_dir: str):
        self.retriever = TfidfRetriever(corpus_dir)

    def answer(self, question: str, top_k_docs: int = 3):
        pipeline_steps = []

        # Step 1: preprocessing (normalization + light query expansion)
        clean_q = _expand_query(question.strip())
        pipeline_steps.append({"step": "Question Preprocessing", "detail": f"Normalized query: \"{clean_q}\""})

        # Step 2: document retrieval (TF-IDF over whole documents)
        retrieved_docs = self.retriever.retrieve_passages(clean_q, top_k=top_k_docs)
        pipeline_steps.append({
            "step": "Document Retrieval (TF-IDF)",
            "detail": f"Retrieved {len(retrieved_docs)} candidate documents ranked by cosine similarity."
        })

        if not retrieved_docs or retrieved_docs[0]["score"] == 0:
            pipeline_steps.append({"step": "Result", "detail": "No relevant documents found in the corpus."})
            return {
                "answer": None,
                "confidence": 0.0,
                "evidence": None,
                "retrieved_documents": retrieved_docs,
                "pipeline": pipeline_steps,
            }

        # Step 3: passage ranking already done via score; take best doc
        best_doc = retrieved_docs[0]
        pipeline_steps.append({
            "step": "Passage Ranking",
            "detail": f"Top passage: '{best_doc['doc_title']}' (score={best_doc['score']})"
        })

        # Step 4: sentence-level selection within the top document(s) for extractive QA
        candidate_sentences = []
        for doc in retrieved_docs:
            sents = self.retriever.retrieve_sentences(clean_q, top_k=3, doc_id=doc["doc_id"])
            candidate_sentences.extend(sents)
        # Reward the requested event, so begin/end questions do not share evidence.
        events = {"end": r"\bend(?:ed|s)?\b", "begin": r"\b(?:began|begin|started)\b"}
        for term, pattern in events.items():
            if re.search(r"\b" + term + r"\b", clean_q, re.I):
                for sentence in candidate_sentences:
                    if re.search(pattern, sentence["text"], re.I):
                        sentence["score"] += 0.35
        candidate_sentences.sort(key=lambda s: s["score"], reverse=True)

        if not candidate_sentences:
            best_sentence_text = best_doc["text"]
            sent_score = best_doc["score"]
        else:
            best_doc = next(d for d in retrieved_docs if d["doc_id"] == candidate_sentences[0]["doc_id"])
            best_sentence_text = candidate_sentences[0]["text"]
            sent_score = candidate_sentences[0]["score"]

        pipeline_steps.append({
            "step": "Evidence Sentence Selection",
            "detail": f"Selected best-matching sentence via TF-IDF similarity (score={round(sent_score,4)})."
        })

        # Step 5: extractive answer span extraction
        answer_text, extraction_conf = extract_answer(clean_q, best_sentence_text)
        overlap = score_sentence_overlap(clean_q, best_sentence_text)
        final_confidence = round(min(0.99, 0.5 * float(sent_score or 0) + 0.3 * extraction_conf + 0.2 * overlap), 2)

        pipeline_steps.append({
            "step": "Extractive Answer Extraction",
            "detail": f"Extracted answer span '{answer_text}' from evidence sentence."
        })

        return {
            "answer": answer_text,
            "confidence": final_confidence,
            "evidence": best_sentence_text,
            "source_document": best_doc["doc_title"],
            "retrieved_documents": retrieved_docs,
            "pipeline": pipeline_steps,
        }

    def list_documents(self):
        return self.retriever.list_documents()
