import sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'extracted_highest'))

import kickmix as km
import dqi_support_facts_r4 as support

print("[*] Converting small DQI to KMX...", flush=True)
c = km.Circuit.from_file(str(ROOT / 'build/test_small_dqi.kmb'), format='kmb')
kmx_in = ROOT / 'build/small_in.kmx'
kmx_out = ROOT / 'build/small_out.kmx'
c.to_file(str(kmx_in), format='kmx')
print(f"[+] Written {kmx_in} ({kmx_in.stat().st_size:,} bytes)", flush=True)

print("[*] Running SupportFacts optimizer...", flush=True)
t0 = time.time()
with open(kmx_in, 'r') as fin, open(kmx_out, 'w') as fout:
    rep = support.optimize_stream(fin, fout)
dur = time.time() - t0

print(f"[+] Optimization finished in {dur:.2f}s:")
print(f"    Rewrites: {rep['rewrites']}")
print(f"    Total rewrites: {rep['rewrite_count']}")

c_opt = km.Circuit.from_file(str(kmx_out), format='kmx')
print(f"[+] Original Toffolis: {c.operation_statistics().num_toffoli_like:,}")
print(f"[+] Optimized Toffolis: {c_opt.operation_statistics().num_toffoli_like:,}")

