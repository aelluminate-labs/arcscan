import requests
from bs4 import BeautifulSoup
import pandas as pd
from config.config import Config
from typing import List, Dict


def extract_table_rows(soup: BeautifulSoup) -> List:
    table = soup.find("table", class_="dextable")
    if not table:
        return []
    return table.find_all("tr")[2:]  # Skip header rows


def detect_table_structure(soup: BeautifulSoup) -> Dict:
    """Detects the structure of the table headers to determine column layout."""
    table = soup.find("table", class_="dextable")
    if not table:
        return {}

    header_cols = table.find_all("tr")[1].find_all("td")
    column_names = [col.text.strip() for col in header_cols]

    return {
        "has_abilities": any("Abilities" in col for col in column_names),
        "has_special": any("Special" in col for col in column_names),
        "required_cols": len(header_cols),
    }


def parse_row_data(row: BeautifulSoup, table_structure: Dict) -> Dict:
    """Parses a single row to extract Pokémon details with consistent column handling."""
    cols = row.find_all("td", class_="fooinfo")
    if len(cols) < table_structure["required_cols"]:
        return {}

    try:
        # Basic info
        no = cols[0].text.strip().lstrip("#").zfill(4)
        name = cols[2].find("a").text.strip()
        types = [
            img["src"].split("/")[-1].split(".")[0] for img in cols[3].find_all("img")
        ]

        # Extract base stats
        base_stats = [stat.text.strip() if stat else "" for stat in cols[4:10]]

        # Ensure we have enough stats
        while len(base_stats) < 6:
            base_stats.append("")

        # Handle Special vs. S.Att/S.Def split
        if table_structure["has_special"]:
            special_value = base_stats[3]
            stats_dict = {
                "HP": base_stats[0],
                "Att": base_stats[1],
                "Def": base_stats[2],
                "S.Att": special_value,  # Map Special to S.Att only
                "S.Def": None,  # Set S.Def to None for Gen 1 Pokemon
                "Spd": base_stats[4],
            }
        else:
            stats_dict = {
                "HP": base_stats[0],
                "Att": base_stats[1],
                "Def": base_stats[2],
                "S.Att": base_stats[3],
                "S.Def": base_stats[4],
                "Spd": base_stats[5],
            }

        # Add abilities if present
        abilities = ""
        if table_structure["has_abilities"] and len(cols) > 10:
            abilities = cols[10].text.strip()

        return {
            "No": no,
            "Name": name,
            "Type": ", ".join(types),
            "Abilities": abilities,
            **stats_dict,
        }
    except Exception as e:
        print(f"Error parsing row: {e}")
        return {}


def fetch_and_extract_pokemon_data(url: str) -> List[Dict]:
    """Fetches and extracts Pokémon data with consistent column handling."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Detect table structure
        table_structure = detect_table_structure(soup)
        if not table_structure:
            print(f"Could not detect table structure for {url}")
            return []

        # Extract rows and parse data
        rows = extract_table_rows(soup)
        pokemon_data = [parse_row_data(row, table_structure) for row in rows]

        return [data for data in pokemon_data if data]  # Filter out empty entries

    except requests.RequestException as e:
        print(f"Request error for {url}: {e}")
    except Exception as e:
        print(f"Error processing {url}: {e}")
    return []


def save_to_csv(data: List[Dict], output_path: str) -> None:
    """Saves Pokémon data with consistent columns to CSV."""
    if not data:
        print("No data available to save.")
        return

    try:
        df = pd.DataFrame(data)
        # Ensure all expected columns are present
        expected_columns = [
            "No",
            "Name",
            "Type",
            "Abilities",
            "HP",
            "Att",
            "Def",
            "S.Att",
            "S.Def",
            "Spd",
        ]
        for col in expected_columns:
            if col not in df.columns:
                df[col] = ""

        # Reorder columns to ensure consistent output
        df = df[expected_columns]
        df.to_csv(output_path, index=False)
        print(f"Data saved successfully to {output_path}")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")


def main() -> None:
    base_url = "https://www.serebii.net/pokedex/"
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
        if pokemon_data:
            print(f"Scraped {len(pokemon_data)} entries from {url}")
            all_pokemon_data.extend(pokemon_data)
        else:
            print(f"No data scraped from {url}")

    if all_pokemon_data:
        output_path = Config.get_output_path("Pokemon")
        save_to_csv(all_pokemon_data, output_path)
    else:
        print("No data was scraped. Please check the webpage structure or URLs.")


if __name__ == "__main__":
    main()
