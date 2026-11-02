import sys
from pathlib import Path
sys.path.insert(0, 'verifiers')
import kickmix as km
import numpy as np

HERE = Path('build/somejoint_src/blocks/dqi/team-1028-narrow240/source')
sys.modules['circ'] = km
sys.path[:0] = [str(HERE), str(HERE / 'exp/r-main/narrow240'), str(HERE / 'playbook/kit/decoder'), str(HERE / 'playbook/kit')]

from final_decoder import decode as ref

print("[*] Testing algebraic relationship between S and (A, B) after forward pass...")
# Let's inspect the exact algebraic representation of A and B
# In ref:
# groups, qs, P, matrix = ref.geometry()
print(f"Matrix rank: {np.linalg.matrix_rank(np.array(ref.matrix, dtype=int))}")
print(f"Matrix shape: {len(ref.matrix)} x {len(ref.matrix[0])}")
