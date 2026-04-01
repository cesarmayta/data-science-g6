import argparse
import csv
import html
import re
import time
from typing import Dict, Iterable, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


BASE_URL = "https://neoauto.com"
LISTINGS_URL = "https://neoauto.com/venta-de-autos-usados"
OUTPUT_CSV = "autos_neoauto_selenium.csv"
TIMEOUT = 30

PROMO_LABELS = (
    "Premium",
    "Ocasión",
    "Ocasion",
    "Como nuevo",
    "Seminuevo",
    "Super equipado",
    "De lujo",
    "Motor Económico",
)

TRANSMISSION_OPTIONS = (
    "Automática - Secuencial",
    "Automatica - Secuencial",
    "Automática",
    "Automatica",
    "Mecánica",
    "Mecanica",
    "Secuencial",
    "CVT",
    "Tiptronic",
    "Manual",
)

FUEL_OPTIONS = (
    "Gasolina-Híbrido",
    "Gasolina-Hibrido",
    "Gasolina Híbrido",
    "Gasolina Hibrido",
    "Gasolina",
    "Diésel",
    "Diesel",
    "Dual",
    "GLP",
    "GNV",
    "Gas",
    "Híbrido",
    "Hibrido",
    "Eléctrico",
    "Electrico",
)

BRAND_MAPPINGS = (
    ("mercedes-benz", "Mercedes-Benz"),
    ("alfa-romeo", "Alfa Romeo"),
    ("aston-martin", "Aston Martin"),
    ("land-rover", "Land Rover"),
    ("rolls-royce", "Rolls-Royce"),
    ("great-wall", "Great Wall"),
    ("jetour", "Jetour"),
    ("volkswagen", "Volkswagen"),
    ("mitsubishi", "Mitsubishi"),
    ("chevrolet", "Chevrolet"),
    ("hyundai", "Hyundai"),
    ("toyota", "Toyota"),
    ("nissan", "Nissan"),
    ("renault", "Renault"),
    ("peugeot", "Peugeot"),
    ("citroen", "Citroen"),
    ("citroën", "Citroen"),
    ("porsche", "Porsche"),
    ("subaru", "Subaru"),
    ("suzuki", "Suzuki"),
    ("volvo", "Volvo"),
    ("mazda", "Mazda"),
    ("lexus", "Lexus"),
    ("bmw", "BMW"),
    ("audi", "Audi"),
    ("jeep", "Jeep"),
    ("kia", "Kia"),
    ("ford", "Ford"),
    ("seat", "Seat"),
    ("mini", "Mini"),
    ("jmc", "JMC"),
    ("jac", "JAC"),
    ("mg", "MG"),
    ("gac", "GAC"),
    ("dfsk", "DFSK"),
    ("chery", "Chery"),
    ("fiat", "Fiat"),
    ("dodge", "Dodge"),
    ("ram", "RAM"),
    ("foton", "Foton"),
    ("byd", "BYD"),
    ("baic", "BAIC"),
)

CSV_COLUMNS = [
    "url_anuncio",
    "imagen_auto",
    "marca",
    "titulo",
    "anio",
    "precio",
    "kilometraje",
    "transmision",
    "combustible",
]


def clean_text(value: Optional[str]) -> str:
    if not value:
        return ""
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def normalize_kilometraje(value: str) -> str:
    match = re.search(r"\b\d[\d.,]*\s*kms?\b", value, flags=re.IGNORECASE)
    if not match:
        match = re.search(r"\b\d[\d.,]*km\b", value, flags=re.IGNORECASE)
    if not match:
        return ""

    digits = re.findall(r"\d+", match.group(0))
    if not digits:
        return ""

    number = f"{int(''.join(digits)):,}"
    return f"{number} km"


def extract_price(value: str) -> str:
    price_match = re.search(r"Precio\s+((?:US\$|S/)\s*[\d.,]+)", value, flags=re.IGNORECASE)
    if price_match:
        return clean_text(price_match.group(1))

    first_currency_match = re.search(r"((?:US\$|S/)\s*[\d.,]+)", value, flags=re.IGNORECASE)
    if first_currency_match:
        return clean_text(first_currency_match.group(1))

    return ""


def extract_year(value: str) -> str:
    match = re.search(r"\b(19|20)\d{2}\b", value)
    return match.group(0) if match else ""


def extract_brand(url: str, title: str) -> str:
    slug = url.rstrip("/").split("/")[-1]
    slug = re.sub(r"-\d+$", "", slug)

    for brand_slug, brand_name in BRAND_MAPPINGS:
        if slug == brand_slug or slug.startswith(brand_slug + "-"):
            return brand_name

    first_token = clean_text(title).split(" ")[0] if title else ""
    return first_token


def find_first_option(text: str, options: Iterable[str]) -> str:
    for option in options:
        pattern = r"\b" + re.escape(option) + r"\b"
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return clean_text(match.group(0))
    return ""


def extract_title(text: str) -> str:
    text = clean_text(text)
    if not text:
        return ""

    for label in PROMO_LABELS:
        if text.lower().startswith(label.lower() + " "):
            text = text[len(label):].strip()
            break

    stop_patterns = [
        r"\bPrecio\b",
        r"\bCon Crédito Vehicular\b",
        r"\bVer detalle\b",
        r"\bContactar\b",
        r"\b\d[\d.,]*\s*kms?\b",
        r"\b\d[\d.,]*km\b",
    ]
    stop_patterns.extend(r"\b" + re.escape(item) + r"\b" for item in TRANSMISSION_OPTIONS)
    stop_patterns.extend(r"\b" + re.escape(item) + r"\b" for item in FUEL_OPTIONS)

    first_stop = len(text)
    for pattern in stop_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match and match.start() < first_stop:
            first_stop = match.start()

    title = text[:first_stop].strip(" -|/")
    return clean_text(title)


def extract_img_url(img: Tag) -> str:
    for attribute in ("src", "data-src", "data-lazy-src", "srcset"):
        value = img.get(attribute)
        if not value:
            continue
        if attribute == "srcset":
            value = value.split(",")[0].strip().split(" ")[0]
        return urljoin(BASE_URL, value)
    return ""


def choose_best_title(candidates: Iterable[str]) -> str:
    cleaned_candidates: List[str] = []
    for candidate in candidates:
        title = extract_title(candidate)
        if title and title not in cleaned_candidates:
            cleaned_candidates.append(title)

    if not cleaned_candidates:
        return ""

    cleaned_candidates.sort(key=lambda item: (len(item), item))
    return cleaned_candidates[0]


def build_record(url: str, image_url: str, raw_text: str) -> Dict[str, str]:
    joined_text = clean_text(raw_text)
    title = extract_title(joined_text)
    return {
        "url_anuncio": urljoin(BASE_URL, url),
        "imagen_auto": image_url,
        "marca": extract_brand(url, title),
        "titulo": title,
        "anio": extract_year(title),
        "precio": extract_price(joined_text),
        "kilometraje": normalize_kilometraje(joined_text),
        "transmision": find_first_option(joined_text, TRANSMISSION_OPTIONS),
        "combustible": find_first_option(joined_text, FUEL_OPTIONS),
    }


def looks_like_listing_anchor(anchor: Tag) -> bool:
    href = anchor.get("href", "")
    return href.startswith("auto/") or href.startswith("/auto/") or "/auto/" in href


def create_empty_record(listing_url: str) -> Dict[str, str]:
    return {
        "url_anuncio": listing_url,
        "imagen_auto": "",
        "marca": "",
        "titulo": "",
        "anio": "",
        "precio": "",
        "kilometraje": "",
        "transmision": "",
        "combustible": "",
    }


def collect_listing_urls(soup: BeautifulSoup) -> Dict[str, Dict[str, str]]:
    listings: Dict[str, Dict[str, str]] = {}
    for anchor in soup.find_all("a", href=True):
        if not looks_like_listing_anchor(anchor):
            continue
        listing_url = urljoin(BASE_URL, anchor["href"])
        listings.setdefault(listing_url, create_empty_record(listing_url))
    return listings


def enrich_listing_with_anchor(record: Dict[str, str], anchor: Tag) -> None:
    detail_text = clean_text(anchor.get_text(" ", strip=True))
    image_tag = anchor.find("img")

    if image_tag is not None and not record["imagen_auto"]:
        record["imagen_auto"] = extract_img_url(image_tag)

    title_candidates = [
        clean_text(anchor.get("aria-label", "")),
        clean_text(anchor.get("title", "")),
        detail_text,
    ]
    descriptor_parts = list(title_candidates)

    if image_tag is not None:
        image_alt = clean_text(image_tag.get("alt", ""))
        image_title = clean_text(image_tag.get("title", ""))
        descriptor_parts.extend([image_alt, image_title])
        title_candidates.extend([image_alt, image_title])

    combined_text = clean_text(" ".join(part for part in descriptor_parts if part))
    if not combined_text:
        return

    parsed = build_record(record["url_anuncio"], record["imagen_auto"], combined_text)
    best_title = choose_best_title(title_candidates)

    if parsed["imagen_auto"] and not record["imagen_auto"]:
        record["imagen_auto"] = parsed["imagen_auto"]
    if best_title and (not record["titulo"] or len(best_title) < len(record["titulo"])):
        record["marca"] = extract_brand(record["url_anuncio"], best_title)
        record["titulo"] = best_title
        record["anio"] = extract_year(best_title)
    elif parsed["titulo"] and not record["titulo"]:
        record["marca"] = parsed["marca"]
        record["titulo"] = parsed["titulo"]
        record["anio"] = parsed["anio"]
    elif parsed["marca"] and not record["marca"]:
        record["marca"] = parsed["marca"]
    if parsed["precio"] and not record["precio"]:
        record["precio"] = parsed["precio"]
    if parsed["kilometraje"] and not record["kilometraje"]:
        record["kilometraje"] = parsed["kilometraje"]
    if parsed["transmision"] and not record["transmision"]:
        record["transmision"] = parsed["transmision"]
    if parsed["combustible"] and not record["combustible"]:
        record["combustible"] = parsed["combustible"]


def parse_listing_cards(soup: BeautifulSoup) -> List[Dict[str, str]]:
    listings = collect_listing_urls(soup)
    for anchor in soup.find_all("a", href=True):
        if not looks_like_listing_anchor(anchor):
            continue
        listing_url = urljoin(BASE_URL, anchor["href"])
        enrich_listing_with_anchor(listings[listing_url], anchor)
    return [record for record in listings.values() if record["titulo"]]


def deduplicate(records: List[Dict[str, str]]) -> List[Dict[str, str]]:
    unique: Dict[str, Dict[str, str]] = {}
    for record in records:
        url = record["url_anuncio"]
        if url not in unique:
            unique[url] = record
            continue

        current = unique[url]
        for key in CSV_COLUMNS[1:]:
            if not current.get(key) and record.get(key):
                current[key] = record[key]

    return list(unique.values())


def create_driver(headless: bool = True) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1440,2200")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"},
    )
    driver.set_page_load_timeout(60)
    return driver


def count_listing_links(page_source: str) -> int:
    soup = BeautifulSoup(page_source, "html.parser")
    urls = {
        a["href"]
        for a in soup.find_all("a", href=True)
        if looks_like_listing_anchor(a)
    }
    return len(urls)


def wait_for_cards(driver: webdriver.Chrome) -> None:
    wait = WebDriverWait(driver, TIMEOUT)
    wait.until(lambda browser: len(browser.find_elements(By.XPATH, "//a[contains(@href, 'auto/')]")) >= 6)


def scroll_to_load_all_cards(driver: webdriver.Chrome, pause_seconds: float = 2.0) -> None:
    stable_rounds = 0
    previous_count = 0

    for _ in range(10):
        current_count = count_listing_links(driver.page_source)
        if current_count == previous_count:
            stable_rounds += 1
        else:
            stable_rounds = 0

        if stable_rounds >= 2:
            break

        previous_count = current_count
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_seconds)


def get_total_pages(driver: webdriver.Chrome) -> int:
    soup = BeautifulSoup(driver.page_source, "html.parser")
    numeric_pages = []
    for anchor in soup.find_all("a"):
        text = clean_text(anchor.get_text())
        if text.isdigit():
            numeric_pages.append(int(text))
    return max(numeric_pages, default=1)


def scrape_page(driver: webdriver.Chrome, page_number: int) -> List[Dict[str, str]]:
    page_url = LISTINGS_URL if page_number == 1 else f"{LISTINGS_URL}?page={page_number}"
    driver.get(page_url)
    wait_for_cards(driver)
    time.sleep(2)
    scroll_to_load_all_cards(driver)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    records = deduplicate(parse_listing_cards(soup))
    print(f"Pagina {page_number}: {len(records)} autos")
    return records


def scrape_all_pages(max_pages: Optional[int], headless: bool) -> List[Dict[str, str]]:
    driver = create_driver(headless=headless)
    try:
        print("Abriendo NeoAuto con Selenium...")
        first_page_records = scrape_page(driver, 1)
        total_pages = get_total_pages(driver)
        pages_to_scrape = min(total_pages, max_pages) if max_pages else total_pages
        print(f"Paginas detectadas: {total_pages}. Se procesaran: {pages_to_scrape}")

        all_records = list(first_page_records)
        for page_number in range(2, pages_to_scrape + 1):
            all_records.extend(scrape_page(driver, page_number))

        return deduplicate(all_records)
    finally:
        driver.quit()


def save_csv(records: List[Dict[str, str]], output_file: str) -> None:
    with open(output_file, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scraper de NeoAuto con Selenium.")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Cantidad maxima de paginas a procesar. Por defecto procesa todas.",
    )
    parser.add_argument(
        "--headful",
        action="store_true",
        help="Abre el navegador con interfaz en lugar de usar modo headless.",
    )
    args = parser.parse_args()

    records = scrape_all_pages(max_pages=args.max_pages, headless=not args.headful)
    if not records:
        raise RuntimeError("No se encontraron autos. Revisa si la estructura de NeoAuto cambió.")

    save_csv(records, OUTPUT_CSV)
    print(f"Se guardaron {len(records)} autos en {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
