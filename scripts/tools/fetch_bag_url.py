import urllib.request
import json

def get_file_url(title):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url|size|mime&format=json"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        pages = data.get('query', {}).get('pages', {})
        for _, v in pages.items():
            if 'imageinfo' in v:
                return v['imageinfo'][0]
    return None

print("Kelly Bag:", get_file_url("File:Red Crocodile Kelly Bag.jpg"))
print("Kelly Bag 2:", get_file_url("File:Kelly Bag.jpg"))
