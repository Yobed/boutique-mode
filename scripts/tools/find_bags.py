import os

for root_dir in [
    r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode",
    r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend"
]:
    for root, dirs, files in os.walk(root_dir):
        if "node_modules" in root or ".git" in root or ".next" in root:
            continue
        for f in files:
            if any(k in f.lower() for k in ["sac", "bag", "handbag", "elsi", "giro"]):
                full = os.path.join(root, f)
                print(f"{os.path.getsize(full):7d} bytes: {full}")
