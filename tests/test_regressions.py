import unittest
from app.services.registry import ir_service, knowledge_service
from app.services.dialogue_manager import DialogueManager
from app.services.evaluation import partial_match
from fastapi.testclient import TestClient
from app.main import app

class RegressionTests(unittest.TestCase):
    def test_end_is_question(self):
        self.assertEqual(DialogueManager.detect_intent('When did World War II end in Europe?'), 'fact_question')
        self.assertEqual(ir_service.answer('When did World War II end in Europe?')['answer'], 'May 8, 1945')

    def test_compound_founders(self):
        self.assertEqual(ir_service.answer('Who founded Microsoft?')['answer'], 'Bill Gates and Paul Allen')

    def test_role_subject(self):
        self.assertEqual(ir_service.answer('Who is the CEO of Microsoft?')['answer'], 'Satya Nadella')

    def test_alias_boundaries(self):
        self.assertIsNone(knowledge_service.detect_entity('What influences sleep?'))

    def test_unsupported_relation(self):
        self.assertIsNone(knowledge_service.query('What is the population of Diabetes?')['answer'])

    def test_context_and_topic_switch(self):
        d = DialogueManager(knowledge_service, ir_service)
        d.handle_message('a', 'What are the symptoms of Diabetes?')
        self.assertEqual(d.handle_message('a', 'What is its treatment?')['relation'], 'treatment')
        r = d.handle_message('a', 'Who created Python?')
        self.assertEqual(r['source'], 'Document Retrieval')
        self.assertEqual(r['response'], 'Guido van Rossum')
        self.assertIsNone(r['session_state']['current_entity'])
        self.assertIsNone(d._get_session('b').current_entity)

    def test_evidence_belongs_to_source(self):
        r = ir_service.answer('Who founded Microsoft?')
        doc = next(d for d in r['retrieved_documents'] if d['doc_title'] == r['source_document'])
        self.assertIn(r['evidence'], doc['text'])

    def test_partial_answer_cannot_pass(self):
        self.assertEqual(partial_match('Bill Gates', 'Bill Gates and Paul Allen'), 0)
        self.assertEqual(partial_match('feverish', 'fever'), 0)

    def test_api(self):
        with TestClient(app) as client:
            self.assertEqual(client.get('/api/health').status_code, 200)
            self.assertEqual(client.post('/api/ir/ask', json={'question': ' '}).status_code, 400)
            self.assertEqual(client.post('/api/ir/ask', json={'question': 'Who created Python?'}).json()['answer'], 'Guido van Rossum')

if __name__ == '__main__': unittest.main()
