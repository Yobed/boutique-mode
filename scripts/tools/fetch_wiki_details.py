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

def get_category_files(cat):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:{cat}&cmnamespace=6&cmlimit=20&format=json"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        return data.get('query', {}).get('categorymembers', [])

print("Shoe info:")
info = get_file_url("File:Merrell Vapor Glove 3.png")
print("Merrell:", info)

print("\nHandbags:")
for m in get_category_files("Handbags"):
    t = m['title']
    if any(t.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
        print(t)
