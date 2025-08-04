import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or \
        (_raise := (_ for _ in ()).throw(RuntimeError("DATABASE_URL not set")))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or \
        (_raise := (_ for _ in ()).throw(RuntimeError("OPENROUTER_API_KEY not set")))
    SECRET_KEY = os.getenv("SECRET_KEY") or \
        (_raise := (_ for _ in ()).throw(RuntimeError("SECRET_KEY is not set")))
