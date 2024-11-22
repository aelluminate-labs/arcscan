import re
from bs4 import BeautifulSoup
from src.utils.extract_text import extract_text


def extract_data_from_card(company):
    # :: Extract details of a company card
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
    # :: Scrape a single page of companies
    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        companies = soup.find_all("div", class_="companyCardWrapper")
        return [extract_data_from_card(company) for company in companies]
    except Exception as e:
        print(f"Error while scraping page {url}: {e}")
        return []
