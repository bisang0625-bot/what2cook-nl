import requests
from bs4 import BeautifulSoup

url = "https://www.ah.nl/bonus"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    print(f"Status Code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    text_content = soup.get_text().lower()
    
    print(f"Page Title: {soup.title.string if soup.title else 'No title'}")
    
    # Check for Speklappen
    if "speklappen" in text_content:
        print("✅ 'Speklappen' found on the page!")
    else:
        print("❌ 'Speklappen' NOT found on the page.")
        
    # Check for 'Next week' link
    links = soup.find_all('a')
    next_week_links = []
    for link in links:
        text = link.get_text()
        if text and ("volgende week" in text.lower() or "next week" in text.lower()):
            next_week_links.append(link.get('href'))
            
    if next_week_links:
        print(f"Found 'Next week' links: {next_week_links}")
    else:
        print("No 'Next week' links found via simple text search.")

except Exception as e:
    print(f"Error: {e}")
