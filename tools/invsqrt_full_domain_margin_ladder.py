"""Exhaustive Full-Domain Evaluation & Margin Ladder for Invsqrt.

Evaluates all 3,133,452 required benchmark inputs against the actual compiled circuit.
Identifies worst-margin inputs, worst ratios, and builds the margin ladder for worst 1, 10, 100 inputs.
Investigates margin doubling potential under ML17 WS9.
"""
from __future__ import annotations

import heapq
import json
import math
from pathlib import Path
import sys
import time
import zipfile

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "verifiers"))

import kickmix as km
import numpy as np
from invsqrt.verify_submission_invsqrt import (
    ProblemSpecInvSqrt,
    validate_registers,
    to_bits,
    reference_values,
    half_turns_to_units,
    rotation_t_count,
    _circuit_sha256,
)

def main():
    print("[*] Extracting candidate invsqrt.kmb...")
    zip_path = REPO_ROOT / "build" / "portfolios" / "portfolio_ml27_repaired.zip"
    temp_dir = REPO_ROOT / "temp_inv_ladder"
    temp_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        z.extract("invsqrt.kmb", temp_dir)
        
    circ_path = temp_dir / "invsqrt.kmb"
    circ = km.Circuit.from_file(str(circ_path))
    circ_hash = _circuit_sha256(circ)
    print(f"    Circuit SHA-256: {circ_hash}")
    print(f"    Active Qubits:   {circ.num_qubits}")
    
    spec = ProblemSpecInvSqrt(
        width=22,
        max_x=3133452,
        beta=1,
        precision_bits=24,
        shots_per_x=1,
        system_qubits=6540
    )
    x_reg, scratch = validate_registers(circ, spec)
    
    max_x = spec.max_x
    batch_size = 4096
    sim = km.Simulator(batch_size=batch_size, counting_operations=False, seed=42)
    
    print(f"[*] Precomputing reference target and tolerance for all {max_x:,} inputs...")
    t_ref0 = time.monotonic()
    all_xs = np.arange(1, max_x + 1, dtype=np.uint64)
    target, tol = reference_values(spec, all_xs)
    print(f"    Reference values precomputed in {time.monotonic() - t_ref0:.2f}s")
    
    print(f"[*] Launching full-domain evaluation over {max_x:,} inputs (batch size: {batch_size})...")
    t0 = time.monotonic()
    
    min_margin_global = 1 << 64
    worst_ratio_global = 0.0
    worst_x_global = 0
    
    # Min-heap to maintain worst 100 margins: stores (-margin, x, ratio, allowed, used)
    # Using negative margin so heap pop removes the least-worst (largest margin)
    worst_100_heap = []
    
    num_batches = (max_x + batch_size - 1) // batch_size
    
    for b in range(num_batches):
        start_x = b * batch_size + 1
        end_x = min((b + 1) * batch_size, max_x)
        actual_count = end_x - start_x + 1
        
        # Prepare batch padded to batch_size
        if actual_count < batch_size:
            xs_batch = np.zeros(batch_size, dtype=np.uint64)
            xs_batch[:actual_count] = np.arange(start_x, end_x + 1, dtype=np.uint64)
            xs_batch[actual_count:] = 1  # Dummy pad
        else:
            xs_batch = np.arange(start_x, end_x + 1, dtype=np.uint64)
            
        sim.clear_for_shot()
        sim.write_across_shots(x_reg, to_bits(xs_batch, spec.width))
        sim.do(circ)
        
        theta = np.array([half_turns_to_units(sim.read_shot_phase(i)) for i in range(actual_count)], dtype=np.uint64)
        
        allowed = tol[start_x - 1 : end_x]
        tgt = target[start_x - 1 : end_x]
        
        error = (theta - tgt).view(np.int64)
        used = np.abs(error).view(np.uint64)
        
        # Check tolerance violations
        bad = np.flatnonzero(used > allowed)
        if len(bad):
            idx = bad[0]
            violation_x = start_x + idx
            raise AssertionError(f"TOLERANCE VIOLATION at x={violation_x}: used={used[idx]} > allowed={allowed[idx]}")
            
        margins = allowed - used
        ratios = np.divide(used, allowed, out=np.zeros(actual_count), where=allowed > 0)
        
        b_min_margin = int(margins.min())
        b_max_ratio = float(ratios.max())
        
        if b_min_margin < min_margin_global:
            min_margin_global = b_min_margin
        if b_max_ratio > worst_ratio_global:
            worst_ratio_global = b_max_ratio
            worst_x_global = int(start_x + np.argmax(ratios))
            
        # Update worst 100
        for i in range(actual_count):
            m_val = int(margins[i])
            r_val = float(ratios[i])
            x_val = int(start_x + i)
            entry = (-m_val, x_val, r_val, int(allowed[i]), int(used[i]))
            if len(worst_100_heap) < 100:
                heapq.heappush(worst_100_heap, entry)
            else:
                if entry > worst_100_heap[0]:
                    heapq.heappushpop(worst_100_heap, entry)
                    
        if (b + 1) % 100 == 0 or (b + 1) == num_batches:
            elapsed = time.monotonic() - t0
            pct = 100.0 * end_x / max_x
            rate = end_x / elapsed
            print(f"    [{pct:5.1f}%] Processed {end_x:,} / {max_x:,} inputs in {elapsed:.1f}s ({rate:,.0f} inputs/s) | Min Margin: {min_margin_global:,} | Worst Ratio: {worst_ratio_global:.6f}")
            
    total_time = time.monotonic() - t0
    print(f"\n[+] Full-Domain Evaluation Complete in {total_time:.2f}s ({max_x / total_time:,.0f} inputs/sec)")
    
    # Sort worst 100 from smallest margin to largest
    sorted_worst = sorted([(-item[0], item[1], item[2], item[3], item[4]) for item in worst_100_heap], key=lambda x: x[0])
    
    print("\n" + "=" * 80)
    print("INVSQRT WORST MARGIN LADDER (WORST 10 INPUTS)")
    print("=" * 80)
    print(f"{'Rank':<5} {'Input x':<10} {'Margin (Units of 2^-64)':<25} {'Ratio (used/tol)':<18} {'Tolerance':<22}")
    print("-" * 80)
    for rank, (m_val, x_val, r_val, all_val, used_val) in enumerate(sorted_worst[:10], start=1):
        print(f"{rank:<5} {x_val:<10} {m_val:<25,d} {r_val:<18.8f} {all_val:<22,d}")
        
    print("\n" + "=" * 80)
    print("MARGIN LADDER SUMMARY:")
    print("=" * 80)
    w1 = sorted_worst[0]
    w10 = sorted_worst[9]
    w100 = sorted_worst[99]
    print(f"  Worst 1   (Rank 1):   x={w1[1]:<10} Margin={w1[0]:,d} (Units of 2^-64) | Ratio={w1[2]:.8f}")
    print(f"  Worst 10  (Rank 10):  x={w10[1]:<10} Margin={w10[0]:,d} (Units of 2^-64) | Ratio={w10[2]:.8f}")
    print(f"  Worst 100 (Rank 100): x={w100[1]:<10} Margin={w100[0]:,d} (Units of 2^-64) | Ratio={w100[2]:.8f}")
    
    # Margin Doubling Analysis
    n_rot = 41
    current_eps = math.pi * min_margin_global / 2**64 / n_rot
    current_t_rot = rotation_t_count(current_eps)
    
    # 1 margin doubling
    eps_2x = current_eps * 2.0
    t_rot_2x = rotation_t_count(eps_2x)
    
    # 2 margin doublings
    eps_4x = current_eps * 4.0
    t_rot_4x = rotation_t_count(eps_4x)
    
    t_saved_1x = n_rot * (current_t_rot - t_rot_2x)
    t_saved_2x = n_rot * (current_t_rot - t_rot_4x)
    
    print("\n" + "=" * 80)
    print("MARGIN DOUBLING SENSITIVITY & COST ANALYSIS (ML17 WS9):")
    print("=" * 80)
    print(f"  Current Min Margin:     {min_margin_global:,d} (turns / 2^64)")
    print(f"  Current Synthesis eps:  {current_eps:.6e}")
    print(f"  Current T-gates / rot:  {current_t_rot:.3f}")
    print(f"  Total Rotation T-gates: {n_rot * current_t_rot:.2f}")
    print(f"  -------------------------------------------------------------")
    print(f"  With 1 Margin Doubling (2x Margin):")
    print(f"    Synthesis eps:        {eps_2x:.6e} (+1 bit)")
    print(f"    T-gates / rot:        {t_rot_2x:.3f} (-0.56 T)")
    print(f"    Net T-Gates Saved:    {t_saved_1x:.2f} T ({t_saved_1x / 4.0:.2f} Toffoli-equiv)")
    print(f"  With 2 Margin Doublings (4x Margin):")
    print(f"    Synthesis eps:        {eps_4x:.6e} (+2 bits)")
    print(f"    T-gates / rot:        {t_rot_4x:.3f} (-1.12 T)")
    print(f"    Net T-Gates Saved:    {t_saved_2x:.2f} T ({t_saved_2x / 4.0:.2f} Toffoli-equiv)")
    
    # Check whether 2 margin doublings are achievable
    # If the worst error ratio is 0.99932, the margin is 1 - 0.99932 = 0.00068 of tol.
    # To double the margin twice (4x margin), error ratio must drop from 0.99932 to 1 - 4*(0.00068) = 0.99728.
    margin_ratio_fraction = float(min_margin_global) / float(w1[3])
    print(f"\n  Worst margin fraction of tolerance: {margin_ratio_fraction * 100.0:.4f}%")
    
    out_json = REPO_ROOT / "ml28" / "invsqrt_margin_ladder_results.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    report_data = {
        "benchmark": "INVSQRT",
        "circuit_sha256": circ_hash,
        "total_inputs_evaluated": max_x,
        "min_margin_units_2_64": min_margin_global,
        "worst_error_over_tol": worst_ratio_global,
        "worst_x": worst_x_global,
        "worst_10": [{"rank": i+1, "x": item[1], "margin": item[0], "ratio": item[2], "tol": item[3], "used": item[4]} for i, item in enumerate(sorted_worst[:10])],
        "margin_doubling": {
            "current_eps": current_eps,
            "current_t_rot": current_t_rot,
            "t_saved_1_doubling": t_saved_1x,
            "toffoli_saved_1_doubling": t_saved_1x / 4.0,
            "t_saved_2_doublings": t_saved_2x,
            "toffoli_saved_2_doublings": t_saved_2x / 4.0,
        }
    }
    with open(out_json, "w") as f:
        json.dump(report_data, f, indent=2)
    print(f"[+] Full-domain margin ladder report written to {out_json}")

if __name__ == "__main__":
    main()
