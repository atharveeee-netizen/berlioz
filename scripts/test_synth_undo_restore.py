import kickmix as km
import numpy as np
import sys
from pathlib import Path

source_dir = Path("build/somejoint_src/blocks/dqi/team-1028-narrow240/source")
sys.path.insert(0, str(source_dir))
sys.path.insert(0, str(source_dir / "playbook/kit/decoder"))
sys.path.insert(0, str(source_dir / "playbook/kit"))
sys.path.insert(0, "verifiers")
sys.modules['circ'] = km

from final_decoder import decode as ref
from dqi.verify_submission_dqi import ProblemSpecDQI, FieldTables, sample_shots, to_bits, optimal_dqi_weights
from exp.decoder.common import ar

spec = ProblemSpecDQI.benchmark_instance()
tables = FieldTables(km.GF2Field(spec.degree))
rng = np.random.default_rng(42)

weight_probs = optimal_dqi_weights(spec.m, spec.max_errors, spec.degree, spec.r) ** 2
syndromes, mbuc, phases = sample_shots(spec, tables, rng, 1, weight_probs)

print("[*] Testing synthesize + undo reversibility on realistic syndrome state...", flush=True)

b = km.CircuitBuilder()
S = [b.alloc_qubits(12) for _ in range(70)]
pole = b.alloc_qubits(1)[0]

C, A, undo = ref.synthesize(b, S, pole)
undo()
b.free(pole)

c = b.finish_circuit()
print(f"[+] Circuit built! Gates={len(c)}, Toffolis={c.operation_statistics().num_toffoli_like}, Qubits={c.num_qubits}", flush=True)

sim = km.Simulator(batch_size=1)
sim.use_same_registers_as(c)

input_syndromes = to_bits(syndromes, spec.degree)
sim.write_across_shots(km.array([q for reg in S for q in reg]), input_syndromes)
sim.do(c)

def read_word(reg):
    bits = sim.read_across_shots(km.array(reg)).flatten()
    return sum(int(bit) << i for i, bit in enumerate(bits))

S_out = [read_word(w) for w in S]

# Check if S_out matches the input:
# Note: words passed to synthesize in ref.decode had linear_words and extraction applied first.
# Here we passed raw S directly into synthesize, so S_out should exactly match S_in!
S_in = syndromes[0].tolist()
matches = (S_out == S_in)
print(f"[+] Exact state match on S: {matches}", flush=True)
if not matches:
    diffs = sum(1 for a, b in zip(S_out, S_in) if a != b)
    print(f"[-] Mismatched words: {diffs} / 70", flush=True)

