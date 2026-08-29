"""
Simple frame-based Dialogue Manager.

Maintains one conversation "frame" per session:
    current_entity, previous_question, previous_answer,
    detected_intent, dialogue_context (last N turns)

Supported intents: greeting, goodbye, help, fact_question,
entity_question, relation_question, clarification, unknown.

Routes fact/entity/relation questions to either the Knowledge Base or the
IR pipeline, and performs simple pronoun coreference resolution
("its", "it", "he", "she", "they" -> current_entity).
"""
import re

GREETING_PATTERNS = re.compile(r"\b(hi|hello|hey|good morning|good afternoon|good evening)\b", re.I)
GOODBYE_PATTERNS = re.compile(r"\b(bye|goodbye|see you|exit|quit|end)\b", re.I)
HELP_PATTERNS = re.compile(r"\b(help|what can you do|how do i use|assist)\b", re.I)
PRONOUN_PATTERN = re.compile(r"\b(its|it|he|she|they|his|her|their|that)\b", re.I)


class DialogueSession:
    def __init__(self):
        self.current_entity = None
        self.previous_question = None
        self.previous_answer = None
        self.detected_intent = None
        self.dialogue_context = []  # list of {role, text}

    def to_dict(self):
        return {
            "current_entity": self.current_entity,
            "previous_question": self.previous_question,
            "previous_answer": self.previous_answer,
            "detected_intent": self.detected_intent,
            "dialogue_context": self.dialogue_context[-6:],
        }


class DialogueManager:
    """In-memory session store keyed by session_id. Suitable for a local demo."""

    def __init__(self, knowledge_service, ir_service):
        self.sessions = {}
        self.knowledge_service = knowledge_service
        self.ir_service = ir_service

    def _get_session(self, session_id: str) -> DialogueSession:
        if session_id not in self.sessions:
            self.sessions[session_id] = DialogueSession()
        return self.sessions[session_id]

    @staticmethod
    def detect_intent(text: str) -> str:
        t = text.strip()
        if GOODBYE_PATTERNS.search(t):
            return "goodbye"
        if HELP_PATTERNS.search(t):
            return "help"
        if GREETING_PATTERNS.search(t) and len(t.split()) <= 4:
            return "greeting"
        if "?" in t or re.match(r"^(who|what|when|where|which|how|why|is|does|do|did)\b", t.lower()):
            return "fact_question"
        return "unknown"

    def resolve_coreference(self, text: str, session: DialogueSession) -> str:
        """Replace pronouns referring to the current entity with the entity name."""
        if session.current_entity and PRONOUN_PATTERN.search(text):
            resolved = PRONOUN_PATTERN.sub(session.current_entity, text)
            return resolved
        return text

    def handle_message(self, session_id: str, message: str):
        session = self._get_session(session_id)
        intent = self.detect_intent(message)
        session.detected_intent = intent

        response_text = None
        source = "Dialogue Manager"
        extra = {}

        if intent == "greeting":
            response_text = "Hello! Ask me a factual question, e.g. 'What is the capital of France?' or 'Who developed the theory of relativity?'"
        elif intent == "goodbye":
            response_text = "Goodbye! Feel free to come back with more questions."
        elif intent == "help":
            response_text = ("I can answer factoid questions using document retrieval (IR-based QA) "
                              "or a structured knowledge base (Knowledge-based QA). "
                              "I also remember context, so you can ask follow-ups like 'What is its population?'.")
        else:
            resolved_message = self.resolve_coreference(message, session)
            was_coreference_resolved = resolved_message != message

            # Try Knowledge Base first (structured, higher precision)
            kb_result = self.knowledge_service.query(resolved_message, context_entity=session.current_entity)

            if kb_result.get("answer") is not None:
                response_text = kb_result.get("answer_sentence", str(kb_result["answer"]))
                source = "Knowledge Base"
                session.current_entity = kb_result.get("entity") or session.current_entity
                extra = {
                    "entity": kb_result.get("entity"),
                    "relation": kb_result.get("relation"),
                    "coreference_resolved": was_coreference_resolved,
                    "resolved_question": resolved_message if was_coreference_resolved else None,
                }
            else:
                # Fall back to IR-based QA
                ir_result = self.ir_service.answer(resolved_message)
                if ir_result.get("answer"):
                    response_text = ir_result["answer"]
                    source = "Document Retrieval"
                    # Try to keep track of an entity mention for future coreference
                    if kb_result.get("entity"):
                        session.current_entity = kb_result.get("entity")
                    extra = {
                        "evidence": ir_result.get("evidence"),
                        "confidence": ir_result.get("confidence"),
                        "coreference_resolved": was_coreference_resolved,
                        "resolved_question": resolved_message if was_coreference_resolved else None,
                    }
                else:
                    response_text = "I couldn't find an answer to that question in the knowledge base or document corpus."
                    source = "Dialogue Manager"

        session.previous_question = message
        session.previous_answer = response_text
        session.dialogue_context.append({"role": "user", "text": message})
        session.dialogue_context.append({"role": "assistant", "text": response_text})

        return {
            "response": response_text,
            "intent": intent,
            "source": source,
            "session_state": session.to_dict(),
            **extra,
        }

    def reset_session(self, session_id: str):
        self.sessions[session_id] = DialogueSession()
        return self.sessions[session_id].to_dict()
