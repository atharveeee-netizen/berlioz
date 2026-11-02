import os
import json
import re

print("Searching for brot in top_solutions notebooks...")
for f in os.listdir("top_solutions"):
    if not f.endswith(".ipynb"):
        continue
    p = os.path.join("top_solutions", f)
    with open(p, "r", encoding="utf-8", errors="ignore") as file_obj:
        text = file_obj.read()
    
    # search for 'brot' in outputs or sources
    brot_matches = re.findall(r'"brot":\s*([0-9]+)', text)
    if brot_matches:
        print(f"{f}: brot values found in json: {set(brot_matches)}")
    else:
        # regex for brot = X
        bm = re.findall(r'brot\s*=\s*([0-9]+)', text)
        if bm:
            print(f"{f}: brot assignments: {set(bm)}")
