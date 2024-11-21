import re
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config.config import Config


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


def scrape_page(url, driver):
    """Scrape a single page of companies."""
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    companies = soup.find_all("div", class_="companyCardWrapper")
    return [extract_data_from_card(company) for company in companies]


# Set up Chrome options
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1200")

# Initialize WebDriver
driver_path = ChromeDriverManager().install()
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Main scraping loop
data = []
try:
    for p in range(1, 2):
        url = f"{Config.URL}&page={p}"
        try:
            page_data = scrape_page(url, driver)
            data.extend(page_data)
            print(f"Page {p} scraped successfully.")
        except Exception as e:
            print(f"Error scraping page {p}: {e}")
        sleep(1)
finally:
    driver.quit()

# Save data to CSV
df = pd.DataFrame(data)
df.to_csv("data/scrapped/data.csv", index=False)
print("Data extraction completed.")
