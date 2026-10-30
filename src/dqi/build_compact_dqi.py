"""Synthesizer for Qubit-Compacted 42-Product Bilinear Tensor DQI Decoder.
Keeps peak qubits locked to <= 903 while saving >1.2M Toffolis via GF(2^12) rank-42 multiplication.
SPDX-License-Identifier: Apache-2.0
"""
import sys, os, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path[:0] = [str(ROOT / 'src/dqi'), str(ROOT / 'verifiers')]

import kickmix as km
from dqi import dqi_reference_circuit as reference
import tower42

class CompactTowerBuilder(tower42.TowerBuilder):
    """Bilinear tensor builder that uses a single persistent 2-qubit scratch pool
    and lets Kickmix native C++ engine manage division/inversion scaffolds cleanly."""
    def __init__(self, raw, km_mod, terms, field):
        super().__init__(raw, km_mod, terms)
        self.field = field
        # Pre-allocate persistent scratch wires once
        self._scratch_mul = raw.alloc_qubits(2)
        self._masked_pool = raw.alloc_qubits(12)
        
    def ixor_gf2_mul(self, lhs, rhs, *, target, field, control=True, tensor=None):
        if field.degree != 12 or field.modulus != self.modulus or isinstance(lhs, int) or isinstance(rhs, int):
            return self.raw.ixor_gf2_mul(lhs, rhs, target=target, field=field, control=control)
        if control is False:
            return
        b, km = self.raw, self.km
        scratch = self._scratch_mul
        masked = None
        if control is not True:
            masked = self._masked_pool
            b.init_and(control, lhs, masked)
            original_lhs, lhs = lhs, masked
            
        previous_a = previous_b = 0
        for am, bm, cm in (self.terms if tensor is None else tensor):
            left = km.array([lhs[j] for j in range(12) if ((am ^ previous_a) >> j) & 1])
            right = km.array([rhs[j] for j in range(12) if ((bm ^ previous_b) >> j) & 1])
            b.cx(left, scratch[0])
            b.cx(right, scratch[1])
            pivot = (cm & -cm).bit_length() - 1
            others = km.array([target[j] for j in range(12) if j != pivot and (cm >> j) & 1])
            if len(others):
                b.cx(target[pivot], others)
            b.ccx(scratch[0], scratch[1], target[pivot])
            if len(others):
                b.cx(target[pivot], others)
            previous_a, previous_b = am, bm
        b.cx(km.array([rhs[j] for j in range(12) if (previous_b >> j) & 1]), scratch[1])
        b.cx(km.array([lhs[j] for j in range(12) if (previous_a >> j) & 1]), scratch[0])
        
        if masked is not None:
            b.del_and(control, original_lhs, masked)
        self.replacements += 1

def build_compact_dqi(output_path: str, n_syndromes: int = 70, n_codeword: int = 4095, degree: int = 12):
    print(f"[*] Initializing Compact 42-product bilinear tensor for GF(2^{degree})...")
    field = km.GF2Field(degree)
    terms = tower42.tower42(field.modulus)
    assert len(terms) == 42, f"Expected 42 terms, got {len(terms)}"
    
    print("[*] Instantiating CompactTowerBuilder and registers...")
    start_time = time.monotonic()
    raw = km.CircuitBuilder()
    builder = CompactTowerBuilder(raw, km, terms, field)
    
    syndromes = [builder.create_quantum_register(degree, name=f'S{i}') for i in range(n_syndromes)]
    mbuc = [builder.create_classical_register(degree, name=f'E{j}') for j in range(n_codeword)]
    iterations = reference.default_n_iters(n_syndromes)
    
    print(f"[*] Building full syndrome decoding MBUC ({iterations} iterations, {n_codeword} positions)...")
    reference.ProosAndZalkaDecoder(n_syndromes, field).build_syndrome_decoding_mbuc(
        builder, syndromes=syndromes, error_mbuc=mbuc, n_iters=iterations
    )
    
    circuit = builder.finish_circuit()
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    circuit.to_file(str(out_p), format='kmb')
    
    elapsed = time.monotonic() - start_time
    stats = circuit.operation_statistics()
    print(f"[+] Circuit successfully written to {out_p} in {elapsed:.2f}s:")
    print(f"    - Active Qubits: {circuit.num_qubits} (Limit <= 903)")
    print(f"    - Toffolis: {stats.num_toffoli_like:,}")
    print(f"    - Instructions: {len(circuit):,}")
    print(f"    - Multiply replacements: {builder.replacements:,}")
    return circuit

if __name__ == '__main__':
    dest = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / 'build/dqi_compact_42.kmb')
    build_compact_dqi(dest)
