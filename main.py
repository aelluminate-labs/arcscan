import pandas as pd
from time import sleep
from config.config import Config
from src.lib.scraper import scrape_page
from src.utils.driver import setup_driver
import random


def main():
    driver = setup_driver()
    output_path = Config.get_output_path("AmbitionBox")

    with open(output_path, mode="a", newline="", encoding="utf-8") as file:
        try:
            # Scraping 100 pages (modify as needed)
            for p in range(1, 100):
                url = f"{Config.URL}&page={p}"
                try:
                    page_data = scrape_page(url, driver)
                    if page_data:
                        page_df = pd.DataFrame(page_data)
                        page_df.to_csv(file, header=file.tell() == 0, index=False)
                        print(f"Page {p} scraped and data saved successfully.")
                except Exception as e:
                    print(f"Error scraping page {p}: {e}")
                sleep(random.uniform(2, 5))
        finally:
            driver.quit()

    print(f"Data extraction completed and saved to {output_path}.")


if __name__ == "__main__":
    main()
