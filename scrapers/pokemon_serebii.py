import requests
from bs4 import BeautifulSoup
import pandas as pd
from config.config import Config
from typing import List, Dict


def extract_table_rows(soup: BeautifulSoup) -> List:
    """Extracts rows from the main Pokémon data table."""
    table = soup.find("table", class_="dextable")
    if not table:
        return []
    return table.find_all("tr")[2:]  # Skip headers


def parse_row_data(row, required_cols: int) -> Dict:
    """Parses a single row to extract Pokémon details."""
    cols = row.find_all("td", class_="fooinfo")
    if len(cols) < required_cols:
        return {}

    try:
        # Pokémon number (pad to 4 digits for consistency)
        no = cols[0].text.strip().lstrip("#").zfill(4)

        # Name
        name = cols[2].find("a").text.strip()

        # Types (if present, extracted from the image src)
        types = [
            img["src"].split("/")[-1].split(".")[0] for img in cols[3].find_all("img")
        ]

        # Abilities (if present in the column, extracted from links)
        abilities = (
            [a.text.strip() for a in cols[4].find_all("a")] if len(cols) > 4 else []
        )

        # Base stats: Match with column names dynamically
        base_stats = [stat.text.strip() if stat else "" for stat in cols[5:11]]

        # Ensure exactly 6 stats, filling in blanks for missing values
        while len(base_stats) < 6:
            base_stats.append("")

        return {
            "No": no,
            "Name": name,
            "Type": ", ".join(types),
            "Abilities": ", ".join(abilities),
            "HP": base_stats[0],
            "Att": base_stats[1],
            "Def": base_stats[2],
            "S.Att": base_stats[3],
            "S.Def": base_stats[4],
            "Spd": base_stats[5],  # Default to blank if missing
        }
    except Exception as e:
        print(f"Error parsing row: {e}")
        return {}


def extract_pokemon_data(soup: BeautifulSoup, required_cols: int) -> List[Dict]:
    """Extracts Pokémon data from the given soup."""
    rows = extract_table_rows(soup)
    return [
        parse_row_data(row, required_cols)
        for row in rows
        if parse_row_data(row, required_cols)
    ]


def fetch_and_extract_pokemon_data(url: str) -> List[Dict]:
    """Fetches and extracts Pokémon data from a given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Attempt extraction with new structure
        pokemon_data = extract_pokemon_data(soup, required_cols=10)
        if pokemon_data:
            return pokemon_data

        # Fallback to old structure
        return extract_pokemon_data(soup, required_cols=11)
    except requests.RequestException as e:
        print(f"Request error for {url}: {e}")
    except Exception as e:
        print(f"Error processing {url}: {e}")
    return []


def save_to_csv(data: List[Dict], output_path: str) -> None:
    """Saves Pokémon data to a CSV file."""
    if not data:
        print("No data available to save.")
        return

    try:
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        print(f"Data saved successfully to {output_path}.")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")


def main() -> None:
    """Main function to scrape Pokémon data and save it to a CSV file."""
    base_url = "https://www.serebii.net/pokedex-gs/"
    types = [
        "bug",
        "dark",
        "dragon",
        "electric",
        "fairy",
        "fighting",
        "fire",
        "flying",
        "ghost",
        "grass",
        "ground",
        "ice",
        "normal",
        "poison",
        "psychic",
        "rock",
        "steel",
        "water",
    ]

    urls = [f"{base_url}{type}.shtml" for type in types]
    all_pokemon_data = []

    for url in urls:
        print(f"Scraping data from {url}...")
        pokemon_data = fetch_and_extract_pokemon_data(url)
        print(f"Scraped {len(pokemon_data)} entries from {url}.")
        all_pokemon_data.extend(pokemon_data)

    if not all_pokemon_data:
        print("No data was scraped. Please check the webpage structure or the URLs.")
        return

    output_path = Config.get_output_path("Pokemon")
    save_to_csv(all_pokemon_data, output_path)


if __name__ == "__main__":
    main()
