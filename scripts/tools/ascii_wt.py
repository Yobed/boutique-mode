import os
from PIL import Image

wt = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Wilfried Telechargement"
for name in ["1dc9a883-7ed7-40be-91fb-de5a035d9ce2.jpeg", "GEL.jpg", "Filtre.jpg", "PEC500.jpg"]:
    p = os.path.join(wt, name)
    im = Image.open(p).convert("L").resize((50, 16))
    chars = " .:-=+*#%@"
    print(f"=== {name} ===")
    for y in range(16):
        line = "".join(chars[im.getpixel((x, y)) * (len(chars)-1) // 255] for x in range(50))
        print(line)
