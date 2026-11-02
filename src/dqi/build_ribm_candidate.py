"""Step 3: Monolithic Compilation of Physical DQI RiBM Candidate Circuit.
Framework: Syzygy Spec-Driven Development Standard (v1.0.0)
Benchmark: Benchmark II — DQI Reed-Solomon RS(4095, 4025, 70) Decoder

Compiles the complete physical .kmb candidate circuit with Kickmix registers:
- S0..S69: 70 quantum syndrome registers (width 12)
- E0..E4094: 4095 classical MBUC outcome registers (width 12)
- Validated qubit budget: Q <= 889 <= 903.

SPDX-License-Identifier: Apache-2.0
"""
import sys
import os
import time
import json
import hashlib
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent.parent.parent
DQI_SRC = ROOT / 'extracted_dqi/blocks/dqi/team-1028-narrow240/source'
sys.path.insert(0, str(DQI_SRC))
sys.path.insert(0, str(DQI_SRC / 'playbook/kit/decoder'))

import kickmix as km
sys.modules['circ'] = km

def build_dqi_ribm_candidate(target_path: str = 'build/circuits/dqi_ribm_candidate.kmb') -> dict:
    target = Path(target_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"[*] Step 3: Starting monolithic compilation to {target}...")
    start_time = time.time()
    
    spec = importlib.util.spec_from_file_location('decoder_under_test', DQI_SRC / 'exp/r-main/narrow240/decode_retimed.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules['decoder_under_test'] = module
    spec.loader.exec_module(module)
    
    b = km.CircuitBuilder()
    S = [b.alloc_qubits(12) for _ in range(70)]
    E = [b.alloc_bits(12) for _ in range(4095)]
    
    print("[*] Lowering decoder DAG and assembling instructions...")
    module.decode(b, S, E)
    
    metadata = []
    for i in range(70):
        metadata.append(f'REGISTER r{i} "S{i}"')
        metadata.extend(f'APPEND_TO_REGISTER q{12 * i + k} r{i}' for k in range(12))
    for j in range(4095):
        metadata.append(f'REGISTER r{70 + j} "E{j}"')
        metadata.extend(f'APPEND_TO_REGISTER b{12 * j + k} r{70 + j}' for k in range(12))
        
    print("[*] Finalizing circuit metadata and serialization...")
    c = km.Circuit('\n'.join(metadata)) + b.finish_circuit()
    c.to_file(str(target), format='kmb')
    
    # Compute SHA-256
    h = hashlib.sha256()
    with open(target, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    digest = h.hexdigest()
    
    ops = c.operation_statistics()
    elapsed = round(time.time() - start_time, 2)
    record = {
        'artifact_path': str(target),
        'sha256': digest,
        'size_bytes': target.stat().st_size,
        'num_qubits': c.num_qubits,
        'static_toffolis': ops.num_toffoli_like,
        'total_instructions': len(c),
        'num_bits': c.num_bits,
        'compilation_seconds': elapsed,
        'qubit_limit_pass': c.num_qubits <= 903
    }
    
    json_path = target.with_suffix('.build.json')
    json_path.write_text(json.dumps(record, indent=2))
    print(f"[+] Circuit compiled successfully in {elapsed}s:")
    print(f"    - SHA-256: {digest}")
    print(f"    - Size: {record['size_bytes']:,} bytes")
    print(f"    - Active Qubits: {c.num_qubits} (Limit <= 903: {record['qubit_limit_pass']})")
    print(f"    - Static Toffolis: {ops.num_toffoli_like:,}")
    return record

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'build/circuits/dqi_ribm_candidate.kmb'
    build_dqi_ribm_candidate(out)
