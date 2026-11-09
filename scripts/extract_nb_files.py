import json, sys, os
from pathlib import Path

nb_path = sys.argv[1]
out_dir = Path(sys.argv[2])
out_dir.mkdir(parents=True, exist_ok=True)

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for i, cell in enumerate(nb.get('cells', [])):
    src = "".join(cell.get('source', []))
    if src.startswith('%%writefile'):
        lines = src.splitlines()
        first_line = lines[0]
        target_path = first_line.replace('%%writefile', '').strip()
        filename = Path(target_path).name
        dest = out_dir / filename
        content = "\n".join(lines[1:])
        dest.write_text(content, encoding='utf-8')
        print(f"[+] Extracted {filename} ({len(content)} bytes)")

