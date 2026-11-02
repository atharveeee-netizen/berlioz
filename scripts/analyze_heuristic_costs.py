import sys
from pathlib import Path
ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT / "verifiers"))

from dfthcsos.verify import heuristic_costs

N = 76
# Lera's shape: R=9, B=143, C=40
R, B, C = 9, 143, 40

print(f"Shape: R={R}, B={B}, C={C}, N={N}")
for brot in [10, 9, 8, 7, 6]:
    try:
        h = heuristic_costs(N, R, B, C, brot)
        print(f"brot={brot:2d}: Toffoli={h['toffoli']:6d}, Persistent={h['persistent_qubits']:3d}, Temp={h['temporary_qubits']:3d}, Total Qubits={h['qubits']:3d}, Cost={h['toffoli']*h['qubits']:12,d}")
    except Exception as e:
        print(f"brot={brot:2d}: Error {e}")

# What about other shapes like R=6, B=144, C=127?
print("\nShape: R=6, B=144, C=127, N=76")
for brot in [10, 9, 8, 7]:
    try:
        h = heuristic_costs(N, 6, 144, 127, brot)
        print(f"brot={brot:2d}: Toffoli={h['toffoli']:6d}, Persistent={h['persistent_qubits']:3d}, Temp={h['temporary_qubits']:3d}, Total Qubits={h['qubits']:3d}, Cost={h['toffoli']*h['qubits']:12,d}")
    except Exception as e:
        print(f"brot={brot:2d}: Error {e}")
