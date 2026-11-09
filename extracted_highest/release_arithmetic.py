"""Rebuild and fully verify the released 95-qubit inverse-square-root circuit.

The fitted signed-digit compiler is credited to Sumit Chongder, script361357149:
https://www.kaggle.com/code/sumitchongder/notebook2f196e646b
Our pinned R4/R5 modules add derivative splitting, top-carry reuse, and early
static-high phase cleanup. A rebuilt artifact always receives its own full
official report; no report is transferred to a different circuit hash.
"""
import hashlib
import json
import math
from pathlib import Path
import time

import private_arithmetic_r4 as r4
import private_arithmetic_r5 as r5

R4_SHA256 = '639d573bf5e2e1f501a959eee1acf477d4567b858dcc1696ed2b72b8c908bada'
R5_SHA256 = 'ba4420ba5348fc2ddf1f32916f144cf29f0b01cdefdab3c6ac5c635f469fc680'
RECORDED_ARTIFACT_SHA256 = 'c1c411a41c4b502e212813ef942815b0149ef3f94f6ecaf3eea48f684e297711'
MAX_VERIFIED_COST = 170991.03969491262
MAX_CONSERVATIVE_COST = 172036.0832069283


def rebuild_public_arithmetic(reference_file, *, output, max_workers=4):
    """Return only a freshly verified, hash-bound artifact at the released cost."""
    assert r4.sha256(r4.__file__) == R4_SHA256
    assert r4.sha256(r5.__file__) == R5_SHA256
    output = Path(output)
    artifact = output / 'invsqrt_rebuilt.kmb'
    assert Path(reference_file).resolve() != artifact.resolve()
    import kickmix as km
    from invsqrt import verify_submission_invsqrt as iv
    output.mkdir(parents=True, exist_ok=True)
    reference = r4.load_reference(reference_file)
    cfg = reference.Cfg(reference.F2, reference.F1, reference.FYR, reference.GY, reference.DROP2)
    tables, _ = reference.build_tables(cfg)
    layout = reference.layout(cfg, tables)
    split, bounds = r4.prepare_split(reference, cfg, tables)
    certificate = r4.integer_certificate(reference, cfg, tables)
    circuit = r5.build_candidate(reference, cfg, tables, layout, split)
    stats = circuit.operation_statistics()
    rotations = int(stats.num_z_pow(min_clifford_hierarchy_level=4))
    assert circuit.num_qubits == 95 and rotations == 44
    epsilon = math.pi * certificate['min_margin_units'] / 2**64 / rotations
    conservative_cost = circuit.num_qubits * (stats.num_toffoli_like +
        (stats.num_t_like + rotations * iv.rotation_t_count(epsilon)) / 4)
    assert math.isfinite(conservative_cost) and conservative_cost <= MAX_CONSERVATIVE_COST + 1e-6
    spec = iv.ProblemSpecInvSqrt.for_n_p(10)
    assert spec.shots_per_x == 64 and spec.num_shots == 200540928
    r4.spot_check(circuit, reference, cfg, tables, spec)
    circuit.to_file(artifact, format='kmb')
    digest = r4.sha256(artifact)
    reloaded = km.Circuit.from_file(artifact, format='kmb')
    started = time.monotonic()
    # Original shots, seed derivation, batch size and verifier cost calculation.
    report = iv.verify(reloaded, spec, max_workers=max_workers)
    assert report['status'] == 'PASS' and report['verified_shots'] == 200540928
    assert report['circuit_sha256'] == digest == r4.sha256(artifact)
    assert report['num_qubits'] == 95 and report['rotation_count'] == 44
    assert math.isfinite(report['score']) and 0 < report['score'] <= MAX_VERIFIED_COST + 1e-6
    assert report['score'] <= conservative_cost + 1e-6
    report['artifact_sha256'] = digest
    report['verification_seconds'] = time.monotonic() - started
    rows = [[e, a, *map(int, tables[e, a])] for e in (0, 1) for a in range(128)]
    table_bytes = json.dumps(rows, separators=(',', ':')).encode()
    audit = {'source_url': 'https://www.kaggle.com/code/sumitchongder/notebook2f196e646b?scriptVersionId=361357149',
             'reference_sha256': r4.REFERENCE_SHA256, 'r4_sha256': R4_SHA256, 'r5_sha256': R5_SHA256,
             'recorded_artifact_sha256': RECORDED_ARTIFACT_SHA256,
             'byte_identical_to_recorded': digest == RECORDED_ARTIFACT_SHA256,
             'coefficient_tables_sha256': hashlib.sha256(table_bytes).hexdigest(),
             'integer_certificate': certificate, 'derivative_bounds': bounds,
             'spot_check_shots': 8192, 'conservative_cost': float(conservative_cost)}
    (output / 'invsqrt_integer_tables.json').write_bytes(table_bytes)
    result = {'selected_circuit': str(artifact), 'report': report, 'audit': audit}
    (output / 'invsqrt_rebuild_verification.json').write_text(json.dumps(result, indent=2))
    return result