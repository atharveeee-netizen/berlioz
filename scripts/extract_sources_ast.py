import json
import os
import ast

nb_path = "top_solutions/somejoint_quantum-circuits-22-77-local-gm-889-qubit-dqi_clean.ipynb"
with open(nb_path, "r", encoding="utf-8", errors="ignore") as f:
    nb = json.load(f)

c6 = "".join(nb['cells'][6]['source'])

# Parse AST of cell 6
tree = ast.parse(c6)
out_dir = "build/somejoint_src"

for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "SOURCES":
                # evaluate value safely
                sources_dict = ast.literal_eval(node.value)
                print(f"Found SOURCES with {len(sources_dict)} files!")
                for rel_path, content in sources_dict.items():
                    full_p = os.path.join(out_dir, rel_path)
                    os.makedirs(os.path.dirname(full_p), exist_ok=True)
                    with open(full_p, "w", encoding="utf-8") as out_f:
                        out_f.write(content)
                print(f"Extracted all {len(sources_dict)} files to {out_dir}")
                break
