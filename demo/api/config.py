from os import environ

import dotenv

dotenv.load_dotenv(override=True)

CLIENT_ID = environ.get("CLIENT_ID")
CLIENT_SECRET = environ.get("CLIENT_SECRET")
MONGODB_URL = environ.get("MONGODB_URL")
OPENAI_API_KEY = environ.get("OPENAI_API_KEY")
DEVELOP = environ.get("DEVELOP") == "true"
MODEL_HOSTS = environ.get("MODEL_HOSTS", "").strip().split()
