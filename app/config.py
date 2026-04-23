import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_PORT = os.getenv("APP_PORT")
    HF_MODEL_URL = os.getenv("HF_MODEL_URL")
    BASE_URL = os.getenv("HF_MODEL_URL")
    LLM_TOKEN = os.getenv("LLM_TOKEN")
    SQLALCHEMY_DATABASE_URI = "sqlite:///db/data.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False