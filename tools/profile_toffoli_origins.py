#!/usr/bin/env python3
"""Hook CircuitBuilder Toffoli methods to find exact callsites in production 889Q DQI.
SPDX-License-Identifier: Apache-2.0
"""
import sys, os, time, json
from pathlib import Path
from collections import Counter

ROOT = Path('c:/Users/noobg/.gemini/antigravity-ide/scratch/berlioz')
DQI_SRC = ROOT / 'extracted_dqi/blocks/dqi/team-1028-narrow240/source'
sys.path.insert(0, str(DQI_SRC))
sys.path.insert(0, str(DQI_SRC / 'playbook/kit/decoder'))

import kickmix as km
sys.modules['circ'] = km

counts = Counter()
orig_ccx = km.CircuitBuilder.ccx
orig_init_and = km.CircuitBuilder.init_and
orig_del_and = km.CircuitBuilder.del_and
orig_cswap = km.CircuitBuilder.cswap
orig_ccz = km.CircuitBuilder.ccz

def get_loc(depth=1):
    f = sys._getframe(depth)
    fname = os.path.basename(f.f_code.co_filename)
    return f"{fname}:{f.f_lineno} ({f.f_code.co_name})"

def spy_ccx(self, *args, **kwargs):
    counts[('ccx', get_loc(1))] += 1
    return orig_ccx(self, *args, **kwargs)

def spy_init_and(self, *args, **kwargs):
    counts[('init_and', get_loc(1))] += 1
    return orig_init_and(self, *args, **kwargs)

def spy_del_and(self, *args, **kwargs):
    counts[('del_and', get_loc(1))] += 1
    return orig_del_and(self, *args, **kwargs)

def spy_cswap(self, *args, **kwargs):
    counts[('cswap', get_loc(1))] += 1
    return orig_cswap(self, *args, **kwargs)

def spy_ccz(self, *args, **kwargs):
    counts[('ccz', get_loc(1))] += 1
    return orig_ccz(self, *args, **kwargs)

km.CircuitBuilder.ccx = spy_ccx
km.CircuitBuilder.init_and = spy_init_and
km.CircuitBuilder.del_and = spy_del_and
km.CircuitBuilder.cswap = spy_cswap
km.CircuitBuilder.ccz = spy_ccz

import importlib.util
spec = importlib.util.spec_from_file_location('decoder_under_test', DQI_SRC / 'exp/r-main/narrow240/decode_retimed.py')
module = importlib.util.module_from_spec(spec)
sys.modules['decoder_under_test'] = module
spec.loader.exec_module(module)

print("[*] Building circuit with direct Toffoli hooks...", flush=True)
t0 = time.time()
b = km.CircuitBuilder()
S = [b.alloc_qubits(12) for _ in range(70)]
E = [b.alloc_bits(12) for _ in range(4095)]
module.decode(b, S, E)
print(f"[*] Done in {time.time()-t0:.2f}s.", flush=True)

print(f"\n[+] Total Toffoli-family calls: {sum(counts.values()):,}", flush=True)
print("\n[+] Top 40 Toffoli Callsites by Gate and Location:", flush=True)
rows = []
for (gate, loc), cnt in counts.most_common(50):
    print(f"    - {gate:<10} {loc:<60} : {cnt:>6}", flush=True)
    rows.append({'gate': gate, 'location': loc, 'count': cnt})

out_p = ROOT / 'ml28/toffoli_callsite_census.json'
out_p.parent.mkdir(parents=True, exist_ok=True)
out_p.write_text(json.dumps(rows, indent=2))
print(f"\n[+] Results saved to {out_p}", flush=True)
