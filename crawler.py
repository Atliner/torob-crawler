import os
import requests
from bs4 import BeautifulSoup
import json
import time
from supabase import create_client, Client

# اتصال امن به سوپابیس با استفاده از متغیرهای محیطی که در گیت‌هاب تعریف کردیم
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def scrape_and_save(product_url, shop_name):
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
        
        # استخراج نام
        title_element = soup.find('h1') or soup.find(attrs={"data-testid": "product-title"})
        title = title_element.text.strip() if title_element else "Unknown Title"
        
        # استخراج قیمت از ساختار JSON-LD
        price = "ناموجود"
        script_tags = soup.find_all('script', type='application/ld+json')
        for tag in script_tags:
            try:
                data = json.loads(tag.string)
                if data.get('@type') == 'Product' or 'offers' in data:
                    offers = data.get('offers', {})
                    if isinstance(offers, list) and len(offers) > 0:
                        price = str(offers[0].get('price', 'ناموجود'))
                    elif isinstance(offers, dict):
                        price = str(offers.get('price', 'ناموجود'))
                    if price != "ناموجود":
                        break
            except Exception:
                continue
                
        # ذخیره یا به‌روزرسانی در دیتابیس Supabase
        data, count = supabase.table("products").upsert({
            "title": title,
            "price": price,
            "shop_name": shop_name,
            "url": product_url,
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }, on_conflict="url").execute()
        
        print(f"✓ Saved in Database: {title} - {price} Toman")

    except Exception as e:
        print(f"An error occurred while scraping or saving: {e}")

# اجرای تست با یک لینک واقعی دیجی‌کالا
if __name__ == "__main__":
    # در اینجا یک لینک واقعی از دیجی‌کالا قرار بده
    test_url = "https://www.digikala.com/product/dkp-11116248/" 
    print("Starting crawler and saving to Supabase...")
    scrape_and_save(test_url, "دیجی‌کالا")
