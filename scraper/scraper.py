import time, random, re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent

class Property24Scraper:
    def __init__(self, base_url, start_page=1, end_page=1):
        self.base_url = base_url
        self.start_page = start_page
        self.end_page = end_page
        self.session = requests.Session()
        self.headers = {
            'User-Agent': UserAgent().random,
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }

    def fetch_page(self, page):
        url = f"{self.base_url}&Page={page}"
        for attempt in range(3):
            try:
                time.sleep(random.uniform(1, 2))
                resp = self.session.get(url, headers=self.headers, timeout=10)
                resp.raise_for_status()
                return resp.text
            except requests.RequestException:
                time.sleep(2 ** attempt)
        return None

    def parse_listing(self, item):
        try:
            title = item.select_one(".p24_title")
            price = item.select_one(".p24_price")
            suburb = item.select_one(".p24_location")
            address = item.select_one(".p24_address")
            features = item.select(".p24_featureDetails")
            size_elem = item.select_one(".p24_size span")
            agent = item.select_one(".p24_branding")
            link_tag = item.select_one("a[href]")

            beds = baths = parking = None
            for feat in features:
                title_attr = feat.get("title", "").lower()
                value = feat.find("span")
                value = int(value.text.strip()) if value and value.text.strip().isdigit() else None

                if "bedroom" in title_attr:
                    beds = value
                elif "bathroom" in title_attr:
                    baths = value
                elif "parking" in title_attr:
                    parking = value

            return {
                "Title": title.text.strip() if title else None,
                "Price": int(re.sub(r"[^\d]", "", price.text)) if price else None,
                "Suburb": suburb.text.strip() if suburb else None,
                "Address": address.text.strip() if address else None,
                "City": "Gauteng",
                "Bedrooms": beds,
                "Bathrooms": baths,
                "Parking": parking,
                "Size": size_elem.text.strip() if size_elem else None,
                "URL": "https://www.property24.com" + link_tag["href"] if link_tag else None,
                "Agent": agent["title"] if agent and agent.has_attr("title") else None
            }
        except Exception as e:
            print(f"❌ Error parsing listing: {e}")
            return None

    def scrape(self):
        listings = []
        for page in range(self.start_page, self.end_page + 1):
            html = self.fetch_page(page)
            if not html:
                continue
            soup = BeautifulSoup(html, 'html.parser')
            items = soup.select(".js_resultTile")
            for item in items:
                listing = self.parse_listing(item)
                if listing:
                    listings.append(listing)
        return pd.DataFrame(listings)
