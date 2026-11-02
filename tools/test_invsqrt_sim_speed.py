import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "verifiers"))
import numpy as np
import kickmix as km
from invsqrt.verify_submission_invsqrt import (
    ProblemSpecInvSqrt,
    validate_registers,
    to_bits,
    reference_values,
    half_turns_to_units,
)

zip_path = Path("build/portfolios/portfolio_ml27_repaired.zip")
import zipfile
with zipfile.ZipFile(zip_path) as z:
    z.extract("invsqrt.kmb", "temp_inv_speed")

c = km.Circuit.from_file("temp_inv_speed/invsqrt.kmb")
spec = ProblemSpecInvSqrt(width=22, max_x=10000, beta=1, precision_bits=24, shots_per_x=1, system_qubits=6540)
x_reg, scratch = validate_registers(c, spec)

batch_size = 2048
num_batches = 10  # 20,480 shots
sim = km.Simulator(batch_size=batch_size, counting_operations=False, seed=42)

t0 = time.monotonic()
for b in range(num_batches):
    xs = np.arange(b * batch_size + 1, (b + 1) * batch_size + 1, dtype=np.uint64)
    sim.clear_for_shot()
    sim.write_across_shots(x_reg, to_bits(xs, spec.width))
    sim.do(c)
    phases = np.array([half_turns_to_units(sim.read_shot_phase(i)) for i in range(batch_size)], dtype=np.uint64)
t1 = time.monotonic()

shots = batch_size * num_batches
dur = t1 - t0
rate = shots / dur
print(f"Executed {shots:,} shots in {dur:.2f}s ({rate:,.1f} shots/sec)")
total_needed = 3133452
est_total_sec = total_needed / rate
print(f"Projected time for full 3,133,452 inputs: {est_total_sec:.1f}s ({est_total_sec / 60.0:.2f} minutes)")
