import os
from PIL import Image

for name in ["image de reference.jpg", "videoframe_6041.png"]:
    p = os.path.join(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images", name)
    im = Image.open(p)
    # print small ascii art (40x20)
    im_small = im.convert("L").resize((50, 20))
    chars = " .:-=+*#%@"
    print(f"=== {name} ===")
    for y in range(20):
        line = "".join(chars[im_small.getpixel((x, y)) * (len(chars)-1) // 255] for x in range(50))
        print(line)
