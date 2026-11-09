"""Reproduce the released DQI artifact using public inputs and fresh verification.

Compiled BM2v3 dependency: k256.dev, claude v1, scriptVersionId=361337610.
https://www.kaggle.com/code/k256net/claude?scriptVersionId=361337610
Exact-control rewrite inspiration: Kirill Tymchishin's QROM/Tower42 notebook.
https://www.kaggle.com/code/kirilltym/quantum-circuits-qrom-tower42
Our contribution is the two certified zero/support-fact compiler passes.
This module requires no private dataset, prior report, or research runner.
"""

import gc
import hashlib
import json
import math
import shutil
import time
from pathlib import Path

BASELINE_SHA256 = 'f41a2fb38f346edc1e0bf5f7b863bf747bdd5579273be94e9ca4c54f269cab8b'
STAGE1_SHA256 = 'd9d3beeb939064ed9e7fdda2bfa338d77de7361e634a3a0ae29396bb79e07c26'
FINAL_SHA256 = 'be01f9ce0549f4f975b4b3031cb73984311d809350aa6246fb2ffd9540ccd09e'
MODULE_SHA256 = {
    'dqi_zero_factors': 'ef66286511427ca524ec74302abb4cfab52bc72a8d6d3dd49e88f32c2023cf1d',
    'dqi_support_facts_r4': 'ff4a930a34317f642ae94c0dfa5caf34949bb0f73a87daf08f570f8747057899',
}


def sha256(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def compile_public_dqi(baseline_kmb, *, output, max_workers=4):
    """Return {selected_circuit, report, audit}; fail closed on any mismatch."""
    import kickmix as km
    from dqi import verify_submission_dqi as dv
    import dqi_zero_factors as zero
    import dqi_support_facts_r4 as support

    baseline, output = Path(baseline_kmb), Path(output)
    assert sha256(baseline) == BASELINE_SHA256
    for module in [zero, support]:
        assert sha256(module.__file__) == MODULE_SHA256[module.__name__]
    assert support.ZeroFactors is zero.ZeroFactors
    stages = [
        (zero, output / 'dqi_stage1.kmb', STAGE1_SHA256, 418, 584026),
        (support, output / 'dqi.kmb', FINAL_SHA256, 280, 583746),
    ]
    source_text, candidate_text = output / '.source.kmx', output / '.candidate.kmx'
    written_paths = [source_text, candidate_text, *(stage[1] for stage in stages),
                     output / 'dqi_verification.json', output / 'dqi_compiler_audit.json']
    assert baseline.resolve() not in {path.resolve() for path in written_paths}
    output.mkdir(parents=True, exist_ok=True)
    assert shutil.disk_usage(output).free >= 4 << 30, 'Need 4 GiB free for bounded official text round trips.'
    audit = {
        'source': 'k256net/claude version 1; scriptVersionId=361337610',
        'baseline_sha256': BASELINE_SHA256, 'compiler_sha256': MODULE_SHA256,
        'kickmix_version': km.__version__, 'self_check': support.self_check(), 'passes': [],
    }
    current = baseline
    try:
        for module, target, expected_hash, rewrites, expected_toffoli in stages:
            circuit = km.Circuit.from_file(str(current), format='kmb')
            circuit.to_file(str(source_text), format='kmx')
            del circuit
            gc.collect()
            assert source_text.stat().st_size <= 3 << 30
            with source_text.open('r') as source, candidate_text.open('w') as destination:
                measured = module.optimize_stream(source, destination, max_seconds=900,
                                                 max_output_bytes=3 << 30)
            source_text.unlink()
            assert measured['rewrites'] == {'CCX': rewrites}
            assert measured['rewrite_count'] == rewrites
            assert candidate_text.stat().st_size <= 3 << 30
            circuit = km.Circuit.from_file(str(candidate_text), format='kmx')
            candidate_text.unlink()
            stats = circuit.operation_statistics()
            assert circuit.num_qubits == 1818 and int(stats.num_toffoli_like) == expected_toffoli
            circuit.to_file(str(target), format='kmb')
            del circuit, stats
            gc.collect()
            assert sha256(target) == expected_hash
            audit['passes'].append({'optimizer': module.__name__, 'rewrite_count': rewrites,
                                    'circuit_sha256': expected_hash, 'max_toffoli_count': expected_toffoli,
                                    'optimization_seconds': measured['seconds']})
            current = target
            print('PUBLIC DQI COMPILER PASS', json.dumps(audit['passes'][-1]), flush=True)
        assert sha256(current) == FINAL_SHA256
        circuit = km.Circuit.from_file(str(current), format='kmb')
        started = time.monotonic()
        report = dv.verify(circuit, dv.ProblemSpecDQI.benchmark_instance(num_shots=102400),
                           max_workers=max_workers)
        report['verification_seconds'] = time.monotonic() - started
        assert report['status'] == 'PASS' and report['verified_shots'] == 102400
        assert report['value_errors'] == report['phase_errors'] == 0
        assert report['circuit_sha256'] == FINAL_SHA256 == sha256(current)
        assert math.isfinite(report['score']) and 0 < report['score'] < 2300794066593.29
        audit['final_sha256'] = FINAL_SHA256
        audit['full_verified_shots'] = report['verified_shots']
        (output / 'dqi_verification.json').write_text(json.dumps(report, indent=2))
        (output / 'dqi_compiler_audit.json').write_text(json.dumps(audit, indent=2))
        print('PUBLIC FULL DQI PASS', json.dumps(report), flush=True)
        return {'selected_circuit': str(current), 'report': report, 'audit': audit}
    finally:
        source_text.unlink(missing_ok=True)
        candidate_text.unlink(missing_ok=True)