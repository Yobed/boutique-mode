import os
from PIL import Image
import numpy as np

def describe_subject(p):
    im = Image.open(p).convert("RGB")
    arr = np.array(im)
    # find pixels that differ from background (assumed near white/gray ~ top-left corner)
    bg = arr[0:10, 0:10, :].mean(axis=(0,1))
    diff = np.linalg.norm(arr.astype(float) - bg, axis=-1)
    mask = diff > 25
    ys, xs = np.where(mask)
    if len(ys) == 0:
        print(f"{os.path.basename(p)}: empty/uniform image")
        return
    min_y, max_y = ys.min(), ys.max()
    min_x, max_x = xs.min(), xs.max()
    obj_arr = arr[min_y:max_y+1, min_x:max_x+1]
    w = max_x - min_x + 1
    h = max_y - min_y + 1
    mean_obj = obj_arr[mask[min_y:max_y+1, min_x:max_x+1]].mean(axis=0)
    print(f"File: {os.path.basename(p)}")
    print(f"  Object bbox: ({min_x}, {min_y}, {max_x}, {max_y}), w={w}, h={h}, AR(w/h)={w/h:.2f}")
    print(f"  Bg color: {bg.astype(int)}, Mean Object color: {mean_obj.astype(int)}")

describe_subject(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\videoframe_6041.png")
describe_subject(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\image de reference.jpg")
describe_subject(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\giro.jpg.jpeg")
describe_subject(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission33\case2_vacuum_thermos.png")
describe_subject(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission33\case3_mechanic_hammer.png")
describe_subject(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission33\case4_ceramic_tea_mug.png")
describe_subject(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission33\case5_tripod_stool.png")
describe_subject(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission33\case6_steam_iron.png")
describe_subject(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission29\case2_nordic_kettle.png")
describe_subject(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission29\case3_table_speaker.png")
describe_subject(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission27\case3_scandinavian_carafe.png")
describe_subject(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission27\case4_timer_front.png")
describe_subject(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission32\case2_ceramic_pitcher_handle.png")
