import sys, zipfile, tempfile
sys.path.insert(0, 'verifiers')
import kickmix as km
import numpy as np

z = zipfile.ZipFile('build/harvest_busyaprime/submission.zip')
with tempfile.TemporaryDirectory() as tmp:
    z.extract('invsqrt.kmb', tmp)
    c_inv = km.Circuit.from_file(f'{tmp}/invsqrt.kmb')
    print("Busyaprime Invsqrt:")
    print(f"  Qubits: {c_inv.num_qubits}")
    stats_inv = c_inv.operation_statistics()
    print(f"  Toffoli-like: {stats_inv.num_toffoli_like}")
    print(f"  T-like: {stats_inv.num_t_like}")
    cost_inv = c_inv.num_qubits * (stats_inv.num_toffoli_like + stats_inv.num_t_like / 4.0)
    print(f"  Static Score estimate: {cost_inv}")
    print(f"  Ratio vs ref (2,076,774.23): {2076774.233715282 / cost_inv:.4f}x")

print("\nChecking dqi_877q.kmb:")
c_877 = km.Circuit.from_file('build/dqi_877q.kmb')
print(f"  Qubits: {c_877.num_qubits}")
stats_877 = c_877.operation_statistics()
print(f"  Toffoli-like: {stats_877.num_toffoli_like}")
print(f"  Total gates: {len(c_877)}")
