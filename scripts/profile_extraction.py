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

print("Profiling extraction reverse...", flush=True)

# Build forward extraction to get token
b = km.CircuitBuilder()
S = [b.alloc_qubits(12) for _ in range(70)]
et = module.extraction(b, S)
c_fwd = b.finish_circuit()
toff_fwd = c_fwd.operation_statistics().num_toffoli_like
print(f"Extraction forward: {toff_fwd} Toffolis")

# Now build reverse extraction
b2 = km.CircuitBuilder()
S2 = [b2.alloc_qubits(12) for _ in range(70)]
# We need token with matching shape:
module.extraction(b2, S2, reverse=True, token=et)
c_rev = b2.finish_circuit()
toff_rev = c_rev.operation_statistics().num_toffoli_like
print(f"Extraction reverse: {toff_rev} Toffolis")

