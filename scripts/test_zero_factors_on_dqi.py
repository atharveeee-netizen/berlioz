import sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'extracted_highest'))

import kickmix as km
import dqi_zero_factors as zero

print("[*] Testing dqi_zero_factors on dqi.kmb...", flush=True)
dqi_path = ROOT / "build/harvest_busyaprime/dqi.kmb"
c = km.Circuit.from_file(str(dqi_path), format='kmb')
print(f"[+] Loaded circuit: {len(c):,} ops, {c.operation_statistics().num_toffoli_like:,} Toffolis", flush=True)

