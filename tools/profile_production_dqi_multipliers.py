#!/usr/bin/env python3
"""Fast Profiler for multiplication callsites in the production 889Q DQI DAG.
SPDX-License-Identifier: Apache-2.0
"""
import sys, os, time, json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path('c:/Users/noobg/.gemini/antigravity-ide/scratch/berlioz')
DQI_SRC = ROOT / 'extracted_dqi/blocks/dqi/team-1028-narrow240/source'
sys.path.insert(0, str(DQI_SRC))
sys.path.insert(0, str(DQI_SRC / 'playbook/kit/decoder'))

import kickmix as km
sys.modules['circ'] = km

from exp.arithmetic import field as ar

# Fast callsite tracking hooks
callsite_counts = Counter()
callsite_ranks = {}

orig_mul_xor0 = ar.mul_xor0
orig_mul_xor = ar.mul_xor

def spy_mul_xor0(b, x, y, z):
    f = sys._getframe(1)
    loc = f"{f.f_code.co_filename.split('/')[-1].split(chr(92))[-1]}:{f.f_lineno} ({f.f_code.co_name})"
    n = len(x)
    callsite_counts[loc] += 1
    if loc not in callsite_ranks:
        callsite_ranks[loc] = len(ar.tensor(n))
    return orig_mul_xor0(b, x, y, z)

def spy_mul_xor(b, x, y, z):
    f = sys._getframe(1)
    loc = f"{f.f_code.co_filename.split('/')[-1].split(chr(92))[-1]}:{f.f_lineno} ({f.f_code.co_name})"
    n = len(x)
    callsite_counts[loc] += 1
    if loc not in callsite_ranks:
        callsite_ranks[loc] = len(ar.tensor(n))
    return orig_mul_xor(b, x, y, z)

ar.mul_xor0 = spy_mul_xor0
ar.mul_xor = spy_mul_xor

import importlib.util
spec = importlib.util.spec_from_file_location('decoder_under_test', DQI_SRC / 'exp/r-main/narrow240/decode_retimed.py')
module = importlib.util.module_from_spec(spec)
sys.modules['decoder_under_test'] = module
spec.loader.exec_module(module)

print("[*] Profiling production 889Q DQI DAG construction...", flush=True)
t0 = time.time()
b = km.CircuitBuilder()
S = [b.alloc_qubits(12) for _ in range(70)]
E = [b.alloc_bits(12) for _ in range(4095)]
module.decode(b, S, E)
print(f"[*] Decoding DAG defined in {time.time()-t0:.2f}s. Finishing circuit...", flush=True)
circ = b.finish_circuit()
elapsed = time.time() - t0

total_calls = sum(callsite_counts.values())
total_toffolis_from_mul = sum(callsite_counts[loc] * callsite_ranks[loc] for loc in callsite_counts)

stats = circ.operation_statistics()

print(f"\n[+] Production Circuit Built in {elapsed:.2f}s:", flush=True)
print(f"    - Peak Qubits: {circ.num_qubits}", flush=True)
print(f"    - Total Instructions: {len(circ):,}", flush=True)
print(f"    - Static Toffolis: {stats.num_toffoli_like:,}", flush=True)
print(f"\n[+] Multiplication Callsite Census:", flush=True)
print(f"    - Total Multiplication Calls in DAG: {total_calls:,}", flush=True)
print(f"    - Total Static Toffolis from Multipliers: {total_toffolis_from_mul:,} ({100*total_toffolis_from_mul/stats.num_toffoli_like:.2f}% of circuit Toffolis)", flush=True)

print("\n[+] Top 20 Callsites by Invocation Count:", flush=True)
for loc, cnt in callsite_counts.most_common(20):
    rank = callsite_ranks[loc]
    toff = cnt * rank
    print(f"    - {loc:<50} | calls: {cnt:>5} | rank: {rank:>3} | toffolis: {toff:>7}", flush=True)

census = {
    'total_circuit_qubits': circ.num_qubits,
    'total_circuit_toffolis': stats.num_toffoli_like,
    'total_multiplier_calls': total_calls,
    'total_multiplier_toffolis': total_toffolis_from_mul,
    'callsites': [
        {'callsite': loc, 'count': cnt, 'rank': callsite_ranks[loc], 'toffolis': cnt * callsite_ranks[loc]}
        for loc, cnt in callsite_counts.most_common()
    ]
}

out_path = ROOT / 'ml28/production_dqi_multiplier_census.json'
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(census, indent=2))
print(f"\n[+] Census saved to {out_path}", flush=True)
