import sys
from pathlib import Path
import numpy as np

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT / "verifiers"))

from dfthcsos.verify import load_inputs, evaluate_words, heuristic_costs

chem_dir = ROOT / "build/ml30_apex_optimum/dfthcsos"
inputs = load_inputs(chem_dir / "submission.npz")
npz = np.load(chem_dir / "submission.npz")
words_10 = npz['angle_words']
tree_edges = npz['tree_edges']

print(f"words_10 shape: {words_10.shape}, min: {words_10.min()}, max: {words_10.max()}")

# Evaluate at brot=10
from dfthcsos.verify import passes_accuracy

m10 = evaluate_words(inputs, words_10, tree_edges, brot=10)
print(f"brot=10: e1={m10['error_1']*1000:.4f} mHa, e2={m10['error_2']*1000:.4f} mHa, lambda={m10['lambda_eff']:.4f}, gap={m10['E_gap']:.4f}, pass={passes_accuracy(m10)}")

# What if we truncate / round words to brot=9, 8, 7?
for b in [9, 8, 7]:
    shift = 10 - b
    words_b = np.round(words_10 / (2**shift)).astype(np.int64)
    words_b = np.clip(words_b, 0, (2**b) - 1)
    mb = evaluate_words(inputs, words_b, tree_edges, brot=b)
    print(f"brot={b:2d} (rounded): e1={mb['error_1']*1000:.4f} mHa, e2={mb['error_2']*1000:.4f} mHa, lambda={mb['lambda_eff']:.4f}, gap={mb['E_gap']:.4f}, pass={passes_accuracy(mb)}")
