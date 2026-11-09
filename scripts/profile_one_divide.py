import sys
from pathlib import Path
import kickmix as km

sys.modules['circ'] = km
sys.path.insert(0, 'verifiers')
sys.path.insert(0, 'build/somejoint_src/blocks/dqi/team-1028-narrow240/source/playbook/kit/decoder')

import importlib.util
HERE = Path('build/somejoint_src/blocks/dqi/team-1028-narrow240/source')

spec_mod = importlib.util.spec_from_file_location('decoder_under_test', HERE / 'exp/r-main/narrow240/decode_retimed.py')
module = importlib.util.module_from_spec(spec_mod)
sys.modules['decoder_under_test'] = module
spec_mod.loader.exec_module(module)

print("decode_retimed loaded successfully!", flush=True)

# Measure divide_fused Toffolis in isolation
b = km.CircuitBuilder()
x = b.alloc_qubits(24)
y = b.alloc_qubits(24)
F = b.alloc_qubits(1)[0]
fm = b.alloc_bits(1)
called = False
def after():
    global called
    called = True

module._divide(b, x, y, F, fm, after, module.ref.folds.K)
c = b.finish_circuit()
toffs = c.operation_statistics().num_toffoli_like
print(f"One divide_fused call: {toffs} Toffolis, {len(c)} instructions, after() called: {called}")
print(f"Across 33 stages: {33 * toffs} Toffolis!")

