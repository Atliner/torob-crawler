# crawler.py
import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_digikala_product(product_url):
    """
    A modern scraper for extracting product details from Digikala.
    Uses robust selectors and standard headers to bypass simple bot detection.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        response = requests.get(product_url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Extract Title
        title_element = soup.find('h1') or soup.find(attrs={"data-testid": "product-title"})
        title = title_element.text.strip() if title_element else "Unknown Title"
        
        # 2. Extract Price (Look for common Persian digit patterns or specific classes)
        # Digikala often embeds JSON-LD or structured data which is way safer to scrape!
        script_tags = soup.find_all('script', type='application/ld+json')
        price = None
        
        for tag in script_tags:
            try:
                data = json.loads(tag.string)
                # Check if it's a product schema
                if data.get('@type') == 'Product' or 'offers' in data:
                    offers = data.get('offers', {})
                    if isinstance(offers, list) and len(offers) > 0:
                        price = offers[0].get('price')
                    elif isinstance(offers, dict):
                        price = offers.get('price')
                    if price:
                        break
            except Exception:
                continue
                
        # Fallback to visual element if JSON-LD fails
        if not price:
            price_element = soup.find(attrs={"data-testid": "price-section"})
            if price_element:
                price = price_element.text.strip()
                
        return {
            "title": title,
            "price": price,
            "url": product_url,
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        print(f"An error occurred while scraping: {e}")
        return None

# Example Usage:
if __name__ == "__main__":
    test_url = "https://www.digikala.com/product/dkp-123456/" # Replace with a real product link
    print("Starting crawler simulation...")
    # data = scrape_digikala_product(test_url)
    # print(data)
