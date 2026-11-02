import zipfile
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "verifiers"))
import numpy as np

temp_dir = Path("temp_audit_ml27")
with zipfile.ZipFile("build/portfolios/portfolio_ml27_repaired.zip") as z:
    z.extractall(temp_dir)

from dfthcsos.verify import load_inputs, evaluate_words
npz_path = temp_dir / "dfthcsos" / "submission.npz"
data = np.load(npz_path)
inp = load_inputs(npz_path)
words = data["angle_words"]
edges = data["tree_edges"]
brot = int(data.get("brot", 8))
res = evaluate_words(inp, words, edges, brot)

print("CHEMISTRY EXACT AUDIT:")
print(f"  error_1: {res['error_1']:.15f} Ha (Limit: 0.020000000000000)")
print(f"  error_2: {res['error_2']:.15f} Ha (Limit: 0.020000000000000)")
print(f"  Margin 1: {0.02 - res['error_1']:.15f} Ha")
print(f"  Margin 2: {0.02 - res['error_2']:.15f} Ha")
print(f"  lambda_eff: {res['lambda_eff']:.15f} Ha")
print(f"  E_gap: {res['E_gap']:.15f} Ha")
print(f"  Passes constraints: {res['error_1'] <= 0.02 and res['error_2'] <= 0.02}")
