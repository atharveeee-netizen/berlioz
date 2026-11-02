import os
import json
import re

for folder in ["src/chem", "top_solutions"]:
    for f in os.listdir(folder):
        p = os.path.join(folder, f)
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8", errors="ignore") as file_obj:
                content = file_obj.read()
            matches = re.findall(r"(?:brot\s*=?\s*7|7-bit|brot\s*<=\s*7|brot7|brot\s*==\s*7)", content, re.IGNORECASE)
            if matches:
                print(f"{p}: {matches[:5]}")
