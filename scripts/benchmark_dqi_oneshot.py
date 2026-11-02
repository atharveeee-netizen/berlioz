import kickmix as km
import time
import sys
from pathlib import Path

source_dir = Path("build/somejoint_src/blocks/dqi/team-1028-narrow240/source")
sys.path.insert(0, str(source_dir))
sys.path.insert(0, str(source_dir / "playbook/kit/decoder"))
sys.path.insert(0, str(source_dir / "playbook/kit"))
sys.path.insert(0, "verifiers")
sys.modules['circ'] = km

from final_decoder import decode as ref
from dqi.verify_submission_dqi import ProblemSpecDQI, FieldTables, sample_shots, to_bits, validate_registers, optimal_dqi_weights, verify

print("[*] Starting reference decoder benchmark test (1 shot)...", flush=True)
t0 = time.time()
spec = ProblemSpecDQI.benchmark_instance(num_shots=1)

b = km.CircuitBuilder()
S = [b.alloc_qubits(12) for _ in range(70)]
E = [b.alloc_bits(12) for _ in range(4095)]

ref.decode(b, S, E)

metadata = []
for i in range(70):
    metadata.append(f'REGISTER r{i} "S{i}"')
    metadata.extend(f'APPEND_TO_REGISTER q{12 * i + k} r{i}' for k in range(12))
for j in range(4095):
    metadata.append(f'REGISTER r{70 + j} "E{j}"')
    metadata.extend(f'APPEND_TO_REGISTER b{12 * j + k} r{70 + j}' for k in range(12))

c = km.Circuit('\n'.join(metadata)) + b.finish_circuit()
t_build = time.time() - t0
print(f"[+] Circuit built in {t_build:.1f}s. Q={c.num_qubits}, Toffolis={c.operation_statistics().num_toffoli_like}, Ops={len(c)}", flush=True)

print("[*] Simulating and verifying with official verifier...", flush=True)
t1 = time.time()
res = verify(c, spec, batch_size=1, log2_delta=-10.0, max_workers=1)
t_sim = time.time() - t1

print(f"[+] Verification completed in {t_sim:.1f}s.", flush=True)
print(f"    Status:       {res['status']}", flush=True)
print(f"    Val errors:   {res['value_errors']}", flush=True)
print(f"    Phase errors: {res['phase_errors']}", flush=True)
print(f"    Toffolis:     {res['toffoli_count']}", flush=True)
print(f"    Score:        {res['score']:.4e}", flush=True)

