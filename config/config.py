import os
import datetime
from dotenv import load_dotenv

load_dotenv()


class Config:
    URL = os.getenv("URL")
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/91.0.864.64",
    ]
    DF_COLUMNS = [
        "company_name",
        "rating",
        "reviews",
        "jobs",
        "interviews",
        "highly_rated_for",
        "critically_rated_for",
    ]

    @staticmethod
    def get_output_path(name):
        now = datetime.datetime.now()
        date_str = now.strftime("%m%d%YT%H%M")
        return f"data/scrapped/{name}_{date_str}.csv"
