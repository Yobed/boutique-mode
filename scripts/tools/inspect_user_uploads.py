import os
from PIL import Image

p1 = r"C:\Users\WILFRIED\.gemini\antigravity\brain\a6afba35-f0a6-4827-a7a0-51c2e154eb99\.user_uploaded\media_1792935373067_b89a04cb.png"
p2 = r"C:\Users\WILFRIED\.gemini\antigravity\brain\a6afba35-f0a6-4827-a7a0-51c2e154eb99\.user_uploaded\media_1792935400525_6ce4f10c.png"

for p in [p1, p2]:
    im = Image.open(p)
    print(f"{os.path.basename(p)}: size={im.size}, mode={im.mode}")
