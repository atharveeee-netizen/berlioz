import sys
from pathlib import Path
sys.path.insert(0, 'verifiers')
import kickmix as km

HERE = Path('build/somejoint_src/blocks/dqi/team-1028-narrow240/source')
sys.modules['circ'] = km
sys.path[:0] = [str(HERE), str(HERE / 'exp/r-main/narrow240'), str(HERE / 'playbook/kit/decoder'), str(HERE / 'playbook/kit')]

from final_decoder import decode as ref

b = km.CircuitBuilder()
S = [b.alloc_qubits(12) for _ in range(70)]
E = [b.alloc_bits(12) for _ in range(4095)]

print("1. Running project...")
mt = ref.baseline.project(b, S, E)

print("2. Running initial...")
ref.linear_words(b, S, ref.matrix)

print("3. Running extract...")
et = ref.extraction(b, S)
print("et keys:", list(et.keys()))

print("4. Running synthesize...")
A, B, undo = ref.synthesize(b, S, et['pole'])
print(f"A: type {type(A)}, len {len(A)}, each element len {[len(x) for x in A]}")
print(f"B: type {type(B)}, len {len(B)}, each element len {[len(x) for x in B]}")
