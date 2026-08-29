"""
Evaluation module.

Runs the IR pipeline and the Knowledge-based pipeline against the local
evaluation_dataset.json and computes real metrics (Exact Match, token-level
F1, Accuracy). Also runs the dialogue manager's intent detector against the
dialogue examples and computes intent accuracy. Nothing here is hardcoded --
every number is derived from actually executing the system.
"""
import json
import re
import string
from collections import Counter


def _normalize(text: str) -> str:
    if text is None:
        return ""
    text = text.lower()
    text = re.sub(r"[{}]".format(re.escape(string.punctuation)), " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def exact_match(pred: str, gold: str) -> int:
    return int(_normalize(pred) == _normalize(gold))


def f1_score(pred: str, gold: str) -> float:
    pred_tokens = _normalize(pred).split()
    gold_tokens = _normalize(gold).split()
    if not pred_tokens or not gold_tokens:
        return float(pred_tokens == gold_tokens)
    common = Counter(pred_tokens) & Counter(gold_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = num_same / len(pred_tokens)
    recall = num_same / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)


def partial_match(pred: str, gold: str) -> int:
    """A softer accuracy signal: gold answer text appears within predicted text or vice versa."""
    p, g = _normalize(pred), _normalize(gold)
    if not p or not g:
        return 0
    return int(g in p or p in g)


class Evaluator:
    def __init__(self, dataset_path: str, ir_service, knowledge_service, dialogue_manager):
        with open(dataset_path, "r", encoding="utf-8") as f:
            self.dataset = json.load(f)
        self.ir_service = ir_service
        self.knowledge_service = knowledge_service
        self.dialogue_manager = dialogue_manager

    def evaluate_ir(self):
        rows = []
        em_scores, f1_scores = [], []
        for item in self.dataset["ir_questions"]:
            result = self.ir_service.answer(item["question"])
            pred = result.get("answer") or ""
            em = exact_match(pred, item["expected_answer"])
            f1 = f1_score(pred, item["expected_answer"])
            correct = bool(em or partial_match(pred, item["expected_answer"]))
            em_scores.append(em)
            f1_scores.append(f1)
            rows.append({
                "question": item["question"],
                "expected_answer": item["expected_answer"],
                "system_answer": pred,
                "exact_match": bool(em),
                "f1": round(f1, 2),
                "correct": correct,
            })
        n = max(1, len(em_scores))
        return {
            "exact_match": round(sum(em_scores) / n, 3),
            "f1": round(sum(f1_scores) / n, 3),
            "total": len(rows),
            "rows": rows,
        }

    def evaluate_kb(self):
        rows = []
        em_scores = []
        for item in self.dataset["kb_questions"]:
            result = self.knowledge_service.query(item["question"])
            pred = result.get("answer") or ""
            em = exact_match(pred, item["expected_answer"])
            correct = bool(em or partial_match(pred, item["expected_answer"]))
            em_scores.append(int(correct))
            rows.append({
                "question": item["question"],
                "expected_answer": item["expected_answer"],
                "system_answer": pred if pred else "(no answer)",
                "correct": correct,
            })
        n = max(1, len(em_scores))
        return {
            "accuracy": round(sum(em_scores) / n, 3),
            "total": len(rows),
            "rows": rows,
        }

    def evaluate_dialogue(self):
        rows = []
        correct = 0
        # Fresh isolated session for repeatable evaluation
        session_id = "__evaluation_session__"
        self.dialogue_manager.reset_session(session_id)
        for item in self.dataset["dialogue_examples"]:
            result = self.dialogue_manager.handle_message(session_id, item["user"])
            predicted_intent = result["intent"]
            is_correct = predicted_intent == item["expected_intent"]
            correct += int(is_correct)
            rows.append({
                "turn": item["turn"],
                "user": item["user"],
                "expected_intent": item["expected_intent"],
                "predicted_intent": predicted_intent,
                "response": result["response"],
                "correct": is_correct,
            })
        n = max(1, len(rows))
        return {
            "intent_accuracy": round(correct / n, 3),
            "total": len(rows),
            "rows": rows,
        }

    def full_report(self):
        return {
            "ir": self.evaluate_ir(),
            "kb": self.evaluate_kb(),
            "dialogue": self.evaluate_dialogue(),
        }
