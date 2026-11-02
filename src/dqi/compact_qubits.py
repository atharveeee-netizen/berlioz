# =============================================================================
# DQI qubit compaction (exact relabeling, no gate changes)
#
# dqi is scored R * Q^2 * T, so every qubit saved is worth ~2x a Toffoli saved
# in relative terms. A scratch qubit is |0> before its first use, right after
# an unconditional HMR or R, and after its last use. This pass cuts every
# scratch qubit's history into segments at those points and packs the
# segments onto the fewest wires (greedy interval colouring, optimal).
# Named registers (S0..S69, E0..E4094) never move; no instruction is added,
# removed or reordered, so Toffoli counts and measurement outcomes are
# unchanged. The new circuit is used only if the official verifier passes it
# with a lower cost.
#
# Run this as the LAST cell of a copy of "Quantum Circuits | Rotation
# Calibration (39 char)" (or any notebook that writes submission.zip).
# =============================================================================
import os, gc, heapq, hashlib, shutil, sys, time, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path[:0] = [str(ROOT / 'verifiers'), str(ROOT)]
import kickmix as km
from dqi import verify_submission_dqi as DV

WORK = ROOT / 'build'
WORKERS = min(4, os.cpu_count() or 1)


def _qubits(tokens):
    return [int(t[1:]) for t in tokens if len(t) > 1 and t[0] == 'q' and t[1:].isdigit()]


def compact_text(text, log=print):
    lines = text.split('\n')
    named, last = set(), {}
    for i, ln in enumerate(lines):
        if not ln or ln[0] == '#':
            continue
        tok = ln.split()
        if tok[0] == 'APPEND_TO_REGISTER':
            if tok[1][0] == 'q':
                named.add(int(tok[1][1:]))
            continue
        if tok[0] == 'REGISTER':
            continue
        for q in _qubits(tok):
            last[q] = i
    all_q = set(last) | named
    n_before = max(all_q) + 1
    free = [w for w in range(n_before) if w not in named]
    heapq.heapify(free)
    wire, depth, peak, nseg = {}, 0, 0, 0
    for i, ln in enumerate(lines):
        if not ln or ln[0] == '#':
            continue
        tok = ln.split()
        op = tok[0]
        if op in ('APPEND_TO_REGISTER', 'REGISTER'):
            continue
        if op == 'PUSH_CONDITION':
            depth += 1; continue
        if op == 'POP_CONDITION':
            depth -= 1; continue
        qs = _qubits(tok)
        if not qs:
            continue
        changed = False
        for q in qs:
            if q in named:
                continue
            if q not in wire:
                wire[q] = heapq.heappop(free); nseg += 1
            if wire[q] != q:
                changed = True
        if len(wire) > peak:
            peak = len(wire)
        if changed:
            lines[i] = ' '.join(('q%d' % (wire.get(int(t[1:]), int(t[1:]))))
                                if (len(t) > 1 and t[0] == 'q' and t[1:].isdigit()) else t for t in tok)
        closes = set()
        if op in ('HMR', 'R') and depth == 0 and 'if' not in tok:
            closes.add(qs[0])
        for q in qs:
            if last.get(q) == i:
                closes.add(q)
        for q in closes:
            if q in wire:
                heapq.heappush(free, wire.pop(q))
    n_after = len(named) + peak if peak else len(named)
    log(f'compaction: {n_before} qubits before; peak live scratch {peak} '
        f'({len(named)} named qubits, {nseg:,} scratch segments)')
    return '\n'.join(lines), n_before


def kmb_sha(circuit, path):
    circuit.to_file(path, format='kmb')
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_standalone():
    archive = ROOT / 'submission.zip'
    if not archive.exists():
        archive = ROOT / 'build/portfolios/submission_ml29_apex.zip'
    print('Source archive:', archive)
    tmp = WORK / 'dqi_compact'
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir()
    with zipfile.ZipFile(archive) as z:
        members = z.namelist()
        (tmp / 'dqi_old.kmb').write_bytes(z.read('dqi.kmb'))

    # ---- 2. compact ---------------------------------------------------------------
    t = time.time()
    old = km.Circuit.from_file(tmp / 'dqi_old.kmb')
    print(f'dqi: {old.num_qubits} qubits, {old.operation_statistics().num_toffoli_like:,} static Toffoli-like')
    text = str(old)
    print(f'text form: {len(text)/1e6:.0f} MB ({time.time()-t:.0f}s)')
    # Round-trip sanity: the unchanged text must rebuild the same circuit bytes.
    rt_ok = kmb_sha(km.Circuit(text), tmp / 'rt.kmb') == hashlib.sha256((tmp / 'dqi_old.kmb').read_bytes()).hexdigest()
    print('text round-trip reproduces the original bytes:', rt_ok)
    new_text, n_before = compact_text(text)
    del text; gc.collect()
    new = km.Circuit(new_text)
    del new_text; gc.collect()
    new.to_file(tmp / 'dqi_new.kmb', format='kmb')
    print(f'compacted circuit: {old.num_qubits} -> {new.num_qubits} qubits, '
          f'{new.operation_statistics().num_toffoli_like:,} static Toffoli-like  ({time.time()-t:.0f}s)')

    # ---- 3. official verification of both ---------------------------------------
    if new.num_qubits >= old.num_qubits:
        print('\nNo qubits saved: the decoder already packs its scratch qubits. submission.zip unchanged.')
    else:
        spec = DV.ProblemSpecDQI.benchmark_instance(num_shots=102400)
        t = time.time()
        r_new = DV.verify(new, spec, max_workers=WORKERS)
        print(f"new dqi:  {r_new['status']}  score {r_new.get('score')}  ({time.time()-t:.0f}s)")
        t = time.time()
        r_old = DV.verify(old, spec, max_workers=WORKERS)
        print(f"old dqi:  {r_old['status']}  score {r_old.get('score')}  ({time.time()-t:.0f}s)")
        if r_new['status'] == 'PASS' and r_new['score'] < r_old['score']:
            gain = r_old['score'] / r_new['score']
            print(f'\ndqi improves {gain:.4f}x  ->  overall score x{gain ** (1/3):.4f}')
            out = WORK / 'submission_new.zip'
            with zipfile.ZipFile(archive) as zin, zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zout:
                for n in members:
                    data = (tmp / 'dqi_new.kmb').read_bytes() if n == 'dqi.kmb' else zin.read(n)
                    zout.writestr(n, data)
            with zipfile.ZipFile(out) as z:
                assert z.testzip() is None and set(z.namelist()) == set(members)
            shutil.move(out, WORK / 'submission.zip')
            print('submission.zip updated with the compacted dqi.kmb')
        else:
            print('\nCompacted circuit did not score better; submission.zip unchanged.')
    shutil.rmtree(tmp, ignore_errors=True)

if __name__ == '__main__':
    run_standalone()