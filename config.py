import os

from dotenv import load_dotenv
import torch
from transformers import WhisperForConditionalGeneration, WhisperProcessor

from src.chat_completions import CompletionExecutor


load_dotenv(override=True)

# Chat Completion
API_KEY = os.getenv("API_KEY")
API_KEY_PRIMARY_VAL = os.getenv("API_KEY_PRIMARY_VAL")
REQUEST_ID = os.getenv("REQUEST_ID")
TEST_APP_ID = os.getenv("TEST_APP_ID")
executor = CompletionExecutor(API_KEY, API_KEY_PRIMARY_VAL, REQUEST_ID, TEST_APP_ID)


# STT
STT_MODEL_NAME = os.getenv("MODEL_NAME")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
PROCESSOR = WhisperProcessor.from_pretrained(STT_MODEL_NAME)
STT_MODEL = WhisperForConditionalGeneration.from_pretrained(STT_MODEL_NAME).to(DEVICE)

# MongoDB
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "admin")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "password")
MONGO_URI = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@localhost:27017/"
DATABASE_NAME = "database"
COLLECTION_NAME = "meetings"