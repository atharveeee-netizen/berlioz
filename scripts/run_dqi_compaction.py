"""Run exact interval-coloring scratch compaction on DQI circuit.
SPDX-License-Identifier: Apache-2.0
"""
import sys, time, gc
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'verifiers'))
sys.path.insert(0, str(ROOT / 'src/dqi'))

import kickmix as km
from dqi import verify_submission_dqi as DV
import compact_qubits as CQ

def main():
    dqi_path = ROOT / 'build/ml29_apex/dqi.kmb'
    print(f'[*] Reading {dqi_path}...')
    t0 = time.time()
    old_c = km.Circuit.from_file(str(dqi_path), format='kmb')
    q_old = old_c.num_qubits
    print(f'[+] Loaded DQI circuit in {time.time()-t0:.1f}s: {q_old} qubits')

    t0 = time.time()
    text = str(old_c)
    del old_c
    gc.collect()
    print(f'[+] Exported text form ({len(text)/1e6:.1f} MB) in {time.time()-t0:.1f}s')

    t0 = time.time()
    new_text, n_before = CQ.compact_text(text, log=print)
    del text
    gc.collect()
    print(f'[+] Compaction analysis done in {time.time()-t0:.1f}s')

    t0 = time.time()
    new_c = km.Circuit(new_text)
    q_new = new_c.num_qubits
    del new_text
    gc.collect()
    print(f'[+] Built new circuit: {q_old} -> {q_new} qubits ({time.time()-t0:.1f}s)')

    if q_new < q_old:
        out_cand = ROOT / 'build/ml29_apex/dqi_compact.kmb'
        new_c.to_file(str(out_cand), format='kmb')
        print(f'[★] Saved compacted DQI circuit to {out_cand}')
        
        # Verify candidate on small test
        print('[*] Verifying compacted circuit on sample shots...')
        spec = DV.ProblemSpecDQI.benchmark_instance(num_shots=512)
        rep = DV.verify(new_c, spec, max_workers=4)
        print(f'[+] Verification result: {rep["status"]} with {rep.get("value_error_count", 0)} value errors, {rep.get("phase_error_count", 0)} phase errors')
    else:
        print('[i] Circuit is already maximally compacted in scratch registers.')

if __name__ == '__main__':
    main()
