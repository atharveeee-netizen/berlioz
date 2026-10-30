#!/usr/bin/env python3
"""CLI synthesizer for the 42-product bilinear tensor DQI decoder circuit.
Builds the RS(4095, 4025) syndrome decoder using measurement-uncomputed tower-field arithmetic.
SPDX-License-Identifier: Apache-2.0
"""
import sys, os, time, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path[:0] = [str(ROOT / 'src/dqi'), str(ROOT / 'verifiers')]

import kickmix as km
from dqi import dqi_reference_circuit as reference
import tower42

def build_42product_dqi(output_path: str, n_syndromes: int = 70, n_codeword: int = 4095, degree: int = 12):
    print(f"[*] Initializing 42-product bilinear tensor for GF(2^{degree})...")
    field = km.GF2Field(degree)
    terms = tower42.tower42(field.modulus)
    assert len(terms) == 42, f"Expected 42 terms, got {len(terms)}"
    
    print("[*] Instantiating FullTowerBuilder and circuit registers...")
    start_time = time.monotonic()
    raw = km.CircuitBuilder()
    builder = tower42.FullTowerBuilder(raw, km, terms, field)
    
    syndromes = [builder.create_quantum_register(degree, name=f'S{i}') for i in range(n_syndromes)]
    mbuc = [builder.create_classical_register(degree, name=f'E{j}') for j in range(n_codeword)]
    iterations = reference.default_n_iters(n_syndromes)
    
    print(f"[*] Building syndrome decoding MBUC ({iterations} iterations)...")
    reference.ProosAndZalkaDecoder(n_syndromes, field).build_syndrome_decoding_mbuc(
        builder, syndromes=syndromes, error_mbuc=mbuc, n_iters=iterations
    )
    
    circuit = builder.finish_circuit()
    assert not builder.inverse_records, "Leaked inverse records remaining!"
    assert not builder.division_records, "Leaked division records remaining!"
    
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    circuit.to_file(str(out_p), format='kmb')
    
    elapsed = time.monotonic() - start_time
    stats = circuit.operation_statistics()
    print(f"[+] Circuit successfully written to {out_p} in {elapsed:.2f}s:")
    print(f"    - Active Qubits: {circuit.num_qubits}")
    print(f"    - Toffolis: {stats.num_toffoli_like:,}")
    print(f"    - Instructions: {len(circuit):,}")
    print(f"    - Multiply replacements: {builder.replacements:,}")
    print(f"    - Inverse replacements: {builder.inverse_replacements:,}")
    print(f"    - Division replacements: {builder.division_replacements:,}")
    return circuit

def main():
    parser = argparse.ArgumentParser(description="Synthesize 42-product DQI decoder circuit.")
    parser.add_argument('output', nargs='?', default=str(ROOT / 'build/dqi.kmb'), help="Destination .kmb path")
    args = parser.parse_args()
    build_42product_dqi(args.output)

if __name__ == '__main__':
    main()
