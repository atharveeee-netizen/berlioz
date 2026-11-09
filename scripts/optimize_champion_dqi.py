import sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'extracted_highest'))

import kickmix as km
import dqi_zero_factors as zero
import dqi_support_facts_r4 as support

dqi_in_kmb = ROOT / 'build/harvest_busyaprime/dqi.kmb'
dqi_out_kmb = ROOT / 'build/dqi_optimized.kmb'
kmx_temp1 = ROOT / 'build/dqi_temp1.kmx'
kmx_temp2 = ROOT / 'build/dqi_temp2.kmx'

print(f"[*] Step 1: Loading {dqi_in_kmb}...", flush=True)
t0 = time.time()
c = km.Circuit.from_file(str(dqi_in_kmb), format='kmb')
stats0 = c.operation_statistics()
print(f"[+] Loaded in {time.time() - t0:.1f}s: {len(c):,} ops, {stats0.num_toffoli_like:,} Toffolis", flush=True)

print(f"[*] Step 2: Exporting to text stream {kmx_temp1}...", flush=True)
t0 = time.time()
c.to_file(str(kmx_temp1), format='kmx')
print(f"[+] Exported in {time.time() - t0:.1f}s ({kmx_temp1.stat().st_size / 1e6:.1f} MB)", flush=True)

print("[*] Step 3: Running Pass 1 (ZeroFactors)...", flush=True)
t0 = time.time()
with open(kmx_temp1, 'r') as fin, open(kmx_temp2, 'w') as fout:
    rep1 = zero.optimize_stream(fin, fout, max_seconds=3600)
print(f"[+] Pass 1 finished in {time.time() - t0:.1f}s: Rewrites = {rep1['rewrite_count']:,}", flush=True)
kmx_temp1.unlink() # Clean up temp1

kmx_temp3 = ROOT / 'build/dqi_temp3.kmx'
print("[*] Step 4: Running Pass 2 (SupportFacts)...", flush=True)
t0 = time.time()
with open(kmx_temp2, 'r') as fin, open(kmx_temp3, 'w') as fout:
    rep2 = support.optimize_stream(fin, fout, max_seconds=3600)
print(f"[+] Pass 2 finished in {time.time() - t0:.1f}s: Rewrites = {rep2['rewrite_count']:,}", flush=True)
kmx_temp2.unlink() # Clean up temp2

print(f"[*] Step 5: Converting back to KMB binary {dqi_out_kmb}...", flush=True)
t0 = time.time()
c_opt = km.Circuit.from_file(str(kmx_temp3), format='kmx')
c_opt.to_file(str(dqi_out_kmb), format='kmb')
kmx_temp3.unlink() # Clean up temp3

stats_opt = c_opt.operation_statistics()
print(f"[+] Written {dqi_out_kmb} in {time.time() - t0:.1f}s:")
print(f"    - Original Toffolis: {stats0.num_toffoli_like:,}")
print(f"    - Optimized Toffolis: {stats_opt.num_toffoli_like:,}")
print(f"    - Net Toffolis Saved: {stats0.num_toffoli_like - stats_opt.num_toffoli_like:,}")
print(f"    - Qubits: {c_opt.num_qubits}")
