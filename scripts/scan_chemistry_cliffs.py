import sys
from pathlib import Path
ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT / "verifiers"))

from dfthcsos.verify import heuristic_costs

N = 76
print("Scanning (R, B, C) for quantum qubit cliffs:")
# Baseline reference: R=9, B=143, C=40
h_base = heuristic_costs(N, 9, 143, 40, 8)
print(f"Base (9, 143, 40, brot=8): Toffoli={h_base['toffoli']}, Temp={h_base['temporary_qubits']}, Q={h_base['qubits']}, T*Q={h_base['toffoli']*h_base['qubits']}")

shapes = [
    (9, 143, 40),
    (9, 128, 40),
    (9, 114, 40),
    (8, 143, 40),
    (8, 128, 40),
    (8, 114, 40),
    (6, 144, 127),
    (10, 129, 46),
    (10, 114, 40),
]

for R, B, C in shapes:
    for brot in [8, 7, 6]:
        try:
            h = heuristic_costs(N, R, B, C, brot)
            cost = h['toffoli'] * h['qubits']
            gain = (h_base['toffoli'] * h_base['qubits']) / cost
            if h['qubits'] < 350 or gain > 1.15:
                print(f"R={R:2d}, B={B:3d}, C={C:3d}, brot={brot:2d} -> Toff={h['toffoli']:5d}, Q={h['qubits']:3d} (Temp={h['temporary_qubits']:3d}), Cost={cost:,}, Gain={gain:.2f}x")
        except Exception:
            pass
