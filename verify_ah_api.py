import requests
import json

# Try checking the API endpoint for bonus items
url = "https://www.ah.nl/bonus/api/segments"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

try:
    print(f"Requesting {url}...")
    response = requests.get(url, headers=headers)
    print(f"API Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API Response received successfully.")
        # Check keys to understand structure
        # print(json.dumps(data, indent=2)[:1000])
        
        # Try to find products
        # This is speculative, structure needs to be inspected
        if 'segments' in data:
            print(f"Found {len(data['segments'])} segments.")
    else:
        print("❌ API request failed.")
        
except Exception as e:
    print(f"Error: {e}")
