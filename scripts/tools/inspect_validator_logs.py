import os

campaign_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\outputs\test_mission37_campaign"
for c in sorted(os.listdir(campaign_dir)):
    lp = os.path.join(campaign_dir, c, "execution.log")
    if os.path.exists(lp):
        with open(lp, "r", encoding="utf-8", errors="ignore") as fp:
            txt = fp.read()
        if "=== STEP 3: GLB VALIDATOR ===" in txt:
            val_section = txt.split("=== STEP 3: GLB VALIDATOR ===")[-1]
            print(f"=== {c} Validator Output ===")
            for line in val_section.strip().splitlines()[:15]:
                print(" ", line)
