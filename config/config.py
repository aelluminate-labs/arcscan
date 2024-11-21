import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DRIVER_PATH = os.getenv("DRIVER_PATH")
    URL = os.getenv("URL")
