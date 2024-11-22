import random
from time import sleep
import requests


def fetch_page_with_retry(url, max_retries=3):
    # :: Fetch a page with retry logic
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.content
            else:
                raise Exception(f"Failed with status code {response.status_code}")
        except Exception as e:
            retries += 1
            print(f"Error: {e}. Retrying... ({retries}/{max_retries})")
            sleep(random.uniform(5, 10))
    raise Exception(f"Max retries reached for {url}")
