import os
from dotenv import load_dotenv

load_dotenv()  # loads variables from a .env file into the process
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # read SECRET_KEY from environment; no default secret is stored in code
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
