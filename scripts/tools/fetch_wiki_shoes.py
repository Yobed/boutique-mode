import urllib.request
import json

def get_category_files(cat):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:{cat}&cmnamespace=6&cmlimit=20&format=json"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        return data.get('query', {}).get('categorymembers', [])

for m in get_category_files("Shoes_on_transparent_background"):
    print(m['title'])
