"""
Knowledge-based QA pipeline (Healthcare domain):

  Question -> Question Understanding -> Entity (Disease) Detection ->
  Relation Detection -> Knowledge Base Query (CSV-backed) ->
  Structured Result -> Natural Language Answer

The knowledge source is `data/healthcare_knowledge_base.csv`: one row per
disease, with columns for symptoms, causes, treatment, specialist, and
prevention. This is loaded into an in-memory entity->relations dict at
startup (equivalent in spirit to loading a table from a database/knowledge
graph), so the query logic itself is agnostic to the storage format.
"""
import csv

RELATION_KEYWORDS = {
    "symptoms": ["symptom", "symptoms", "signs", "sign", "how do i know", "feel like"],
    "causes": ["cause", "causes", "caused by", "why do", "reason for", "what causes"],
    "treatment": ["treatment", "treat", "cure", "medicine", "how to treat", "how is it treated", "remedy"],
    "specialist": ["doctor", "specialist", "which doctor", "who should i see", "which physician"],
    "prevention": ["prevent", "prevention", "avoid", "how to avoid", "how can i prevent"],
    "category": ["type of disease", "category", "what type", "what kind of disease", "what is"],
}


class KnowledgeService:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.entities = {}
        self.alias_lookup = []
        self._load_csv()

    def _load_csv(self):
        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["entity"].strip()
                aliases = [a.strip().lower() for a in row.get("aliases", "").split(",") if a.strip()]
                relations = {
                    "category": row.get("category", "").strip(),
                    "symptoms": row.get("symptoms", "").strip(),
                    "causes": row.get("causes", "").strip(),
                    "treatment": row.get("treatment", "").strip(),
                    "specialist": row.get("specialist", "").strip(),
                    "prevention": row.get("prevention", "").strip(),
                }
                self.entities[name] = {"type": "Disease", "relations": relations}
                for alias in set(aliases) | {name.lower()}:
                    self.alias_lookup.append((alias, name))

        # Longest alias first, so "type 2 diabetes" matches before "diabetes"
        self.alias_lookup.sort(key=lambda x: len(x[0]), reverse=True)

    def detect_entity(self, question: str):
        q_lower = question.lower()
        for alias, canonical in self.alias_lookup:
            if alias in q_lower:
                return canonical
        return None

    def detect_relation(self, question: str, entity: str = None):
        q_lower = question.lower()
        best_relation = None
        best_len = 0
        available_relations = set()
        if entity and entity in self.entities:
            available_relations = set(self.entities[entity]["relations"].keys())

        for relation, keywords in RELATION_KEYWORDS.items():
            if available_relations and relation not in available_relations:
                continue
            for kw in keywords:
                if kw in q_lower and len(kw) > best_len:
                    best_relation = relation
                    best_len = len(kw)
        return best_relation

    def query(self, question: str, context_entity: str = None):
        pipeline_steps = []
        pipeline_steps.append({"step": "Question Understanding", "detail": f"Parsed question: \"{question}\""})

        entity = self.detect_entity(question)
        resolved_via_context = False
        if not entity and context_entity:
            entity = context_entity
            resolved_via_context = True

        pipeline_steps.append({
            "step": "Entity Detection",
            "detail": (f"Detected entity: {entity}" + (" (resolved from conversation context)" if resolved_via_context else ""))
                       if entity else "No known disease entity detected in the question."
        })

        if not entity or entity not in self.entities:
            pipeline_steps.append({"step": "Result", "detail": "Entity not found in knowledge base."})
            return {
                "answer": None, "entity": entity, "relation": None,
                "source": "Healthcare Knowledge Base (CSV)", "record": None,
                "pipeline": pipeline_steps,
            }

        relation = self.detect_relation(question, entity)
        pipeline_steps.append({
            "step": "Relation Detection",
            "detail": f"Detected relation: {relation}" if relation else "No matching relation keyword found; defaulting to overview."
        })

        if not relation:
            relation = "category"

        if relation not in self.entities[entity]["relations"] or not self.entities[entity]["relations"][relation]:
            pipeline_steps.append({"step": "Result", "detail": f"No stored value for relation '{relation}' on '{entity}'."})
            return {
                "answer": None, "entity": entity, "relation": relation,
                "source": "Healthcare Knowledge Base (CSV)",
                "record": self.entities[entity]["relations"],
                "pipeline": pipeline_steps,
            }

        value = self.entities[entity]["relations"][relation]
        pipeline_steps.append({
            "step": "Knowledge Base Query (CSV)",
            "detail": f"Queried record: {entity} --[{relation}]--> {value[:60]}{'...' if len(value) > 60 else ''}"
        })

        answer_text = self._to_natural_language(entity, relation, value)
        pipeline_steps.append({"step": "Natural Language Answer", "detail": answer_text})

        return {
            "answer": value,
            "answer_sentence": answer_text,
            "entity": entity,
            "relation": relation,
            "source": "Healthcare Knowledge Base (CSV)",
            "record": {relation: value},
            "full_record": self.entities[entity]["relations"],
            "pipeline": pipeline_steps,
        }

    @staticmethod
    def _to_natural_language(entity, relation, value):
        templates = {
            "symptoms": f"Common symptoms of {entity} include: {value}.",
            "causes": f"{entity} is typically caused by: {value}.",
            "treatment": f"{entity} is usually treated with: {value}.",
            "specialist": f"For {entity}, you should typically consult a {value}.",
            "prevention": f"{entity} can be prevented by: {value}.",
            "category": f"{entity} is classified as a {value}.",
        }
        return templates.get(relation, f"{entity}'s {relation} is {value}.")

    def list_entities(self):
        return [
            {"name": name, "type": data["type"], "relations": [r for r, v in data["relations"].items() if v]}
            for name, data in self.entities.items()
        ]
