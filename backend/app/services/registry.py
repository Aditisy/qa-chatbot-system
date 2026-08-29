"""
Central place that instantiates all services once (loading the corpus and
knowledge base is not free, so we do it a single time at process start) and
exposes them for the API routers and evaluation script to share.
"""
import os

from .ir_service import IRService
from .knowledge_service import KnowledgeService
from .dialogue_manager import DialogueManager
from .evaluation import Evaluator

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
CORPUS_DIR = os.path.join(DATA_DIR, "ir_documents")
KB_PATH = os.path.join(DATA_DIR, "healthcare_knowledge_base.csv")
EVAL_DATASET_PATH = os.path.join(DATA_DIR, "evaluation_dataset.json")

ir_service = IRService(CORPUS_DIR)
knowledge_service = KnowledgeService(KB_PATH)
dialogue_manager = DialogueManager(knowledge_service, ir_service)
evaluator = Evaluator(EVAL_DATASET_PATH, ir_service, knowledge_service, dialogue_manager)
