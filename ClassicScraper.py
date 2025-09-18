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

    def get_product_info(self, siv_code):
        """
        Vrátí tuple (name, category). Pokud něco chybí, vrátí None pro chybějící hodnotu.
        """
        try:
            url = f"https://shop.api.de/product/details/{siv_code}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Název produktu: <div id="product_details_stats"><h5 class="fw-bold ...">...</h5>
            name_el = soup.select_one('#product_details_stats h5.fw-bold')
            name = name_el.get_text(strip=True) if name_el else None

            # Kategorie (Warengruppe) – najít <div> se stringem 'Warengruppe' a vzít následující sibling <div><b>...</b>
            label_div = soup.find('div', string='Warengruppe')
            category = None
            if label_div:
                value_b = label_div.find_next_sibling('div')
                if value_b:
                    b = value_b.find('b')
                    if b:
                        category = b.get_text(strip=True)

            return name, category

        except Exception as e:
            print(f"Chyba při zpracování {siv_code}: {str(e)}")
            return None, None

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

