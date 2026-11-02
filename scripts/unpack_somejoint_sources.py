import json
import os
import ast
import re

nb_path = "top_solutions/somejoint_quantum-circuits-22-77-local-gm-889-qubit-dqi_clean.ipynb"
with open(nb_path, "r", encoding="utf-8", errors="ignore") as f:
    nb = json.load(f)

c6 = "".join(nb['cells'][6]['source'])

# Find SOURCES = {...}
# Let's extract the SOURCES dict safely
pattern = r"SOURCES\s*=\s*(\{.*?\})\s*BUILDS"
match = re.search(pattern, c6, re.DOTALL)
if match:
    sources_str = match.group(1)
    # Parse with ast.literal_eval
    sources = ast.literal_eval(sources_str)
    print(f"Successfully parsed SOURCES with {len(sources)} files!")
    out_dir = "build/somejoint_src"
    for rel_path, content in sources.items():
        full_p = os.path.join(out_dir, rel_path)
        os.makedirs(os.path.dirname(full_p), exist_ok=True)
        with open(full_p, "w", encoding="utf-8") as out_f:
            out_f.write(content)
    print(f"Extracted all files to {out_dir}")
else:
    print("Could not find SOURCES in cell 6 with regex, trying alternate parsing...")
    # Let's look for SOURCES = {
    start = c6.find("SOURCES = {")
    if start != -1:
        # Find closing } before BUILDS
        end = c6.find("BUILDS = [", start)
        sub = c6[start+10:end].strip()
        if sub.endswith(";"): sub = sub[:-1]
        # parse dict
        parsed = ast.literal_eval("{" + sub)
        print(f"Parsed {len(parsed)} files from slice!")
        out_dir = "build/somejoint_src"
        for rel_path, content in parsed.items():
            full_p = os.path.join(out_dir, rel_path)
            os.makedirs(os.path.dirname(full_p), exist_ok=True)
            with open(full_p, "w", encoding="utf-8") as out_f:
                out_f.write(content)
        print(f"Extracted all files to {out_dir}")
