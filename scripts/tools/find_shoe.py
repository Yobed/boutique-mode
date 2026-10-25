import os

wt = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Wilfried Telechargement"
keywords = ["shoe", "chaussure", "sneaker", "boot", "escarpin", "basket", "talon", "bottine", "derby", "mocassin", "sandale"]

for root, dirs, files in os.walk(wt):
    for f in files:
        fl = f.lower()
        if any(k in fl for k in keywords):
            print("Found:", os.path.join(root, f))
