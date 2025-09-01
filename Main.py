# Main.py
import os
import time
from Database import Database
from ClassicScraper import ClassicScraper


def main():
    mode = input("Chcete automatický (a) nebo ruční (r) režim? [a/r]: ").lower()
    auto_mode = mode == 'a'

    scraper = ClassicScraper()
    db = Database()

    try:
        db.connect()
        db.create_ignored_table()

        # Načtení ignorovaných kódů
        ignored_codes = scraper.load_ignored_codes()
        if ignored_codes:
            db.insert_ignored_codes(ignored_codes)

        # Získání produktů
        products = db.get_products()

        updates = []
        new_ignored = []

        for product in products:
            siv_code = product['SivCode']
            print(f"\nZpracovávám produkt: {siv_code}")

            category = scraper.get_category(siv_code)

            if not category:
                print("→ Kategorie nenalezena, přidávám do ignorovaných")
                new_ignored.append(siv_code)
                continue

            # Překlad kategorie
            translated_category = scraper.translate_category(category)
            print(f"→ Nalezena kategorie: {category} → {translated_category}")

            updates.append((translated_category, siv_code))

            if not auto_mode:
                user_input = input("Enter - pokračovat, 'quit' - ukončit: ").strip()
                if user_input.lower() == 'quit':
                    break
            else:
                time.sleep(0.5)  # Krátká pauza v automatickém režimu

        # Uložení změn
        if updates:
            db.update_products(updates)
            print(f"\nUloženo {len(updates)} produktů")

        if new_ignored:
            scraper.save_ignored_codes(new_ignored)
            print(f"Přidáno {len(new_ignored)} nových ignorovaných kódů")

    except Exception as e:
        print(f"Došlo k chybě: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()