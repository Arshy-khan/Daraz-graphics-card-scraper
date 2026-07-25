import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    print("Daraz opening for full extraction...")
    driver.get("https://www.daraz.pk/catalog/?q=graphics+card")
    time.sleep(5)
    
    # Page scroll down to load all dynamic elements
    driver.execute_script("window.scrollTo(0, 1500);")
    time.sleep(3)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    products = soup.select('[data-qa-locator="product-item"]')
    
    cards_list = []
    
    for item in products:
        try:
            # 1. Title & Link Extraction
            title = "N/A"
            link = "N/A"
            title_tag = item.find('a', id=lambda x: x and x.startswith('id-a-')) or item.find('a', title=True)
            if title_tag:
                title = title_tag.get('title') or title_tag.text.strip()
                link = title_tag.get('href')
                if link and not link.startswith('http'):
                    link = "https:" + link
            
            if title == "N/A" or not title:
                img_tag = item.find('img')
                if img_tag and img_tag.get('alt'):
                    title = img_tag.get('alt').strip()

            # 2. Price Extraction
            price = "N/A"
            price_tag = item.find('span', string=lambda text: text and 'Rs.' in text)
            if price_tag:
                price = price_tag.text.strip()

            # 3. Rating & Reviews Extraction
            rating = "N/A"
            reviews = "N/A"
            
            # Rating stars / score search
            rating_tag = item.find('span', {'class': 'ratting--x_Piy'}) or item.find('div', {'class': 'rating'})
            if rating_tag:
                rating = rating_tag.text.strip()
                
            # Total reviews count search
            review_tag = item.find('span', string=lambda text: text and ('(' in text or 'Reviews' in text))
            if review_tag:
                reviews = review_tag.text.strip().replace('(', '').replace(')', '')

            if title != "N/A" and title != "":
                cards_list.append({
                    "Product Name": title,
                    "Price": price,
                    "Rating": rating,
                    "Total Reviews": reviews,
                    "Product Link": link
                })
        except Exception:
            continue

    if cards_list:
        df = pd.DataFrame(cards_list)
        output_filename = "Daraz_Graphic_Cards_Advanced.xlsx"
        df.to_excel(output_filename, index=False)
        print(f"Success! Advanced data with Ratings & Reviews saved in '{output_filename}'.")
    else:
        print("No product data extracted!")

finally:
    driver.quit()
