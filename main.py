import re
import random
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config.config import Config
import requests
import time

# :: Randomly select a user agent
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/91.0.864.64",
]
random_user_agent = random.choice(user_agents)


def extract_text(tag, class_name=None):
    """Extract and return text from a tag if it exists."""
    element = tag.find(class_name=class_name) if class_name else tag
    return element.text.strip() if element else None


def extract_data_from_card(company):
    """Extract details of a company card."""
    company_name = extract_text(
        company.find("h2", class_="companyCardWrapper__companyName")
    )
    rating = extract_text(company.find("div", class_="rating_text"))

    reviews = extract_text(
        company.find("a", href=re.compile("reviews")).find(
            "span", class_="companyCardWrapper__ActionCount"
        )
    )
    jobs = extract_text(
        company.find("a", href=re.compile("jobs")).find(
            "span", class_="companyCardWrapper__ActionCount"
        )
    )
    interviews = extract_text(
        company.find("a", href=re.compile("interviews")).find(
            "span", class_="companyCardWrapper__ActionCount"
        )
    )

    highly_rated_for, critically_rated_for = None, None
    rating_wrapper = company.find(
        "div", class_="companyCardWrapper__ratingComparisonWrapper"
    )
    if rating_wrapper:
        highly_rated_section = rating_wrapper.find(
            "span", class_="companyCardWrapper__ratingHeader--high"
        )
        if highly_rated_section:
            highly_rated_for = extract_text(
                highly_rated_section.find_next(
                    "span", class_="companyCardWrapper__ratingValues"
                )
            )

        critically_rated_section = rating_wrapper.find(
            "span", class_="companyCardWrapper__ratingHeader--critical"
        )
        if critically_rated_section:
            critically_rated_for = extract_text(
                critically_rated_section.find_next(
                    "span", class_="companyCardWrapper__ratingValues"
                )
            )

    return {
        "company_name": company_name,
        "rating": rating,
        "reviews": reviews,
        "jobs": jobs,
        "interviews": interviews,
        "highly_rated_for": highly_rated_for,
        "critically_rated_for": critically_rated_for,
    }


def fetch_page_with_retry(url, max_retries=3):
    """Fetch a page with retry logic."""
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url)  # Make an HTTP request to fetch the page
            if response.status_code == 200:
                return response.content  # Return the content if successful
            else:
                raise Exception(f"Failed with status code {response.status_code}")
        except Exception as e:
            retries += 1
            print(f"Error: {e}. Retrying... ({retries}/{max_retries})")
            sleep(random.uniform(5, 10))  # Sleep with random backoff
    raise Exception(f"Max retries reached for {url}")


def scrape_page(url, driver):
    """Scrape a single page of companies."""
    try:
        driver.get(url)  # Using Selenium to load the page in the browser
        soup = BeautifulSoup(
            driver.page_source, "html.parser"
        )  # Parse the page with BeautifulSoup
        companies = soup.find_all(
            "div", class_="companyCardWrapper"
        )  # Find all company cards
        return [extract_data_from_card(company) for company in companies]
    except Exception as e:
        print(f"Error while scraping page {url}: {e}")
        return []  # Return empty list in case of error


# Set up Chrome options
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1200")
options.add_argument(f"user-agent={random_user_agent}")

# Initialize WebDriver
driver_path = ChromeDriverManager().install()
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Initialize a CSV file to store data progressively
output_path = "data/scrapped/data.csv"
df_columns = [
    "company_name",
    "rating",
    "reviews",
    "jobs",
    "interviews",
    "highly_rated_for",
    "critically_rated_for",
]

# Open the CSV file for appending and writing headers if necessary
with open(output_path, mode="a", newline="", encoding="utf-8") as file:
    writer = pd.DataFrame(columns=df_columns)

    # Main scraping loop
    try:
        for p in range(1, 100):  # Scraping 100 pages (modify as needed)
            url = f"{Config.URL}&page={p}"
            try:
                page_data = scrape_page(url, driver)
                if page_data:
                    page_df = pd.DataFrame(page_data)
                    page_df.to_csv(
                        file, header=file.tell() == 0, index=False
                    )  # Write data to CSV incrementally
                    print(f"Page {p} scraped and data saved successfully.")
            except Exception as e:
                print(f"Error scraping page {p}: {e}")
            sleep(random.uniform(2, 5))  # Sleep to avoid overloading the server
    finally:
        driver.quit()  # Quit the driver when done

print(f"Data extraction completed and saved to {output_path}.")
