# Arcscan

Arcscan is a versatile web scraping tool designed to automate data collection processes from various online sources. It efficiently extracts valuable information from websites, making it ideal for web research, data analysis, and building datasets from publicly available web content.


###### NOTE: This project is currently in the development stage and will be updated frequently.

## Features

- **Automated Data Collection**: ArcScan automates the process of extracting data from websites, saving time and effort.
- **Random User Agent**: The tool randomly selects a user agent to mimic different browsers, helping to avoid detection by anti-scraping mechanisms.
- **Retry Logic**: Includes retry logic to handle temporary network issues or server errors, ensuring data collection is robust.
- **Selenium Integration**: Uses Selenium for browser automation, allowing for dynamic content loading and interaction.
- **BeautifulSoup Parsing**: Leverages BeautifulSoup for HTML parsing, making it easy to extract structured data from web pages.
- **Progressive Data Storage**: Data is stored progressively in a CSV file, allowing for incremental updates and resumption of interrupted scraping sessions.

## Installation

To set up Arcscan, follow these steps:

1. Clone the repository:

```bash
git clone https://github.com/yourusername/arcscan.git
cd arcscan
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Set Up ChromeDriver:
   
   - Ensure you have Chrome installed on your system.
   - The project uses webdriver_manager to automatically manage the ChromeDriver installation.


## Configuration

Before running the script, you need to configure the `config.config.Config` class with the appropriate URL and any other necessary settings.

## Usage

Arcscan includes different modules for scraping data from various sources. 

| Module | URL Link | Description | Command To Run | Output |
| ------ | ----------- | ------- | ------ | ------ |
| **Pokémon Serebii Scraper** | [www.serebii.net](https://www.serebii.net/) | Scrapes Pokémon data from Serebii.net | `python -m scrapers.pokemon_serebii` | `data/scrapped/pokemon_<timestamp>.csv.` |
| **AmbitionBox Scraper** | [ambitionbox.com](https://www.ambitionbox.com/) | Scrapes company reviews from AmbitionBox | `python -m scrapers.ambitionbox` | `data/scrapped/ambitionbox_<timestamp>.csv.` |


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Acknowledgments

- Thanks to the developers of **BeautifulSoup**, **Selenium**, and other libraries used in this project.

## Activity

![Alt](https://repobeats.axiom.co/api/embed/70f2fb5653e8d752d82dd865ec5fc6532ff7f491.svg "Repobeats analytics image")