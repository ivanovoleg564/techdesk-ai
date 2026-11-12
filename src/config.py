import os
from dotenv import load_dotenv

load_dotenv()

APP_MODE = os.getenv("APP_MODE", "mock")

GIGACHAT_CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS")