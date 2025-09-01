# ClassicScraper.py
import requests
import json
from bs4 import BeautifulSoup


class ClassicScraper:
    def __init__(self):
        self.translate_map = {
            "Headsets": "Sluchátka s mikrofonem",
            # Další překlady můžete přidat zde
        }
        self.ignored_file = "ignored_SivCodes.json"

    def get_category(self, siv_code):
        try:
            url = f"https://shop.api.de/product/details/{siv_code}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            category_div = soup.find('div', string='Warengruppe')

            if category_div:
                category = category_div.find_next_sibling('div').find('b')
                return category.text.strip() if category else None

        except Exception as e:
            print(f"Chyba při zpracování {siv_code}: {str(e)}")

        return None

    def translate_category(self, category):
        return self.translate_map.get(category, category)

    def load_ignored_codes(self):
        try:
            with open(self.ignored_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_ignored_codes(self, new_codes):
        existing = self.load_ignored_codes()
        updated = list(set(existing + new_codes))

        with open(self.ignored_file, 'w') as f:
            json.dump(updated, f, indent=2)