import requests
from bs4 import BeautifulSoup

class ESGScraper:
    def fetch_article_text(self, url: str) -> str:
        headers = {
            # This makes the website think you are a real Chrome browser
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }
        try:
            print(f"🕵️ Scraping: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status() # Check if we got a 403 or 404
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for paragraph tags
            paragraphs = soup.find_all('p')
            text = " ".join([p.get_text() for p in paragraphs])
            
            if len(text) < 100:
                print("⚠️ Warning: Scraped text is very short. Might be blocked.")
            return text
        except Exception as e:
            print(f"❌ Scraper Error: {e}")
            return ""