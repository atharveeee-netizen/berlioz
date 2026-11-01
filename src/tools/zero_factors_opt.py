"""Exact control-absorption and zero-factor rewrite pass for Kickmix KMX circuits.
Adapted from verified public control propagation by Kirill Tymchishin / Artem Nazemtsev.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
import collections
import re
import time
from pathlib import Path

QUBIT = re.compile(r'q[0-9]+\Z')
ARITY = {'R': 1, 'X': 1, 'CX': 2, 'CCX': 3, 'Z': 1, 'CZ': 2, 'CCZ': 3, 'SWAP': 2, 'CSWAP': 3}


class ZeroFactors:
    """F(q) contains unchanged controls c for which c=0 implies q=0.

    Versioned references invalidate a factor whenever its control is written.
    Facts are valid only within one uninterrupted supported instruction region.
    Consequently classical condition changes and unsupported quantum operations
    cannot carry a fact into another control context.
    """
    def __init__(self):
        self.versions = collections.defaultdict(int)
        self.factors = {}
        self.constants = {}
        self.changes = collections.Counter()
        self.examples = []
        self.opcodes = collections.Counter()
        self.unknown_examples = {}

    def clear(self):
        self.versions.clear()
        self.factors.clear()
        self.constants.clear()

    def valid(self, factors):
        return {item for item in factors if self.versions[item[0]] == item[1]}

    def get(self, q):
        return self.valid(self.factors.get(q, set())) | {(q, self.versions[q])}

    def write(self, q, factors=(), constant=None):
        self.versions[q] += 1
        self.factors[q] = set(sorted(self.valid(factors))[:32])
        if constant is None:
            self.constants.pop(q, None)
        else:
            self.constants[q] = constant

    def product(self, controls):
        if any(self.constants.get(q) == 0 for q in controls):
            return None
        remaining = [q for q in controls if self.constants.get(q) != 1]
        changed = True
        while changed and len(remaining) > 1:
            changed = False
            for q in remaining:
                if any(other != q and (q, self.versions[q]) in self.get(other) for other in remaining):
                    remaining.remove(q)
                    changed = True
                    break
        return remaining

    def xor_target(self, controls, target):
        if any(self.constants.get(q) == 0 for q in controls):
            return
        known = all(self.constants.get(q) == 1 for q in controls)
        old_constant = self.constants.get(target)
        if known:
            self.write(target, constant=None if old_constant is None else old_constant ^ 1)
            return
        product_factors = set().union(*(self.get(q) for q in controls))
        factors = product_factors if old_constant == 0 else self.get(target) & product_factors
        self.write(target, factors)

    def rewrite(self, line: str, number: int) -> str:
        words = line.split()
        if not words or words[0] == 'INFO_TAG':
            return line
        op, args = words[0], words[1:]
        self.opcodes[op] += 1
        if op not in ARITY or len(args) != ARITY[op] or not all(QUBIT.fullmatch(q) for q in args) or len(set(args)) != len(args):
            self.unknown_examples.setdefault(op, line.strip()[:180])
            self.clear()
            return line
        replacement = None
        reason = None
        if op == 'R':
            self.write(args[0], constant=0)
        elif op == 'X':
            q = args[0]
            old = self.constants.get(q)
            self.write(q, constant=None if old is None else old ^ 1)
        elif op in {'CX', 'CCX'}:
            controls, target = args[:-1], args[-1]
            simple = self.product(controls)
            if op == 'CCX' and simple != controls:
                replacement = '' if simple is None else ('X ' + target if not simple else 'CX ' + simple[0] + ' ' + target)
                reason = 'zero or implied Toffoli control'
            self.xor_target(controls, target)
        elif op in {'Z', 'CZ', 'CCZ'}:
            simple = self.product(args)
            if op == 'CCZ' and simple != args:
                if simple is None:
                    replacement = ''
                elif not simple:
                    replacement = 'Z ' + args[0]
                else:
                    replacement = ('Z' if len(simple) == 1 else 'CZ') + ' ' + ' '.join(simple)
                reason = 'zero or implied phase control'
        elif op == 'SWAP':
            a, b = args
            fa, fb = self.get(a), self.get(b)
            ca, cb = self.constants.get(a), self.constants.get(b)
            self.versions[a] += 1
            self.versions[b] += 1
            self.factors[a], self.factors[b] = self.valid(fb), self.valid(fa)
            self.constants.pop(a, None)
            self.constants.pop(b, None)
            if cb is not None:
                self.constants[a] = cb
            if ca is not None:
                self.constants[b] = ca
        elif op == 'CSWAP':
            control, a, b = args
            ca, cb, cc = self.constants.get(a), self.constants.get(b), self.constants.get(control)
            both_masked = ((control, self.versions[control]) in self.get(a)
                           and (control, self.versions[control]) in self.get(b))
            if cc == 0 or ca == cb == 0:
                replacement = ''
                reason = 'inactive Fredkin swap'
            else:
                fa, fb = self.get(a), self.get(b)
                if cc == 1 or both_masked:
                    replacement = 'SWAP ' + a + ' ' + b
                    reason = 'implied Fredkin control'
                shared = fa & fb
                self.versions[a] += 1
                self.versions[b] += 1
                self.factors[a] = self.valid(fb if cc == 1 or both_masked else shared)
                self.factors[b] = self.valid(fa if cc == 1 or both_masked else shared)
                self.constants.pop(a, None)
                self.constants.pop(b, None)
                if cc == 1 or both_masked:
                    if cb is not None:
                        self.constants[a] = cb
                    if ca is not None:
                        self.constants[b] = ca
                elif ca is not None and ca == cb:
                    self.constants[a] = self.constants[b] = ca
        if replacement is None:
            return line
        self.changes[op] += 1
        if len(self.examples) < 80:
            self.examples.append({'line': number, 'before': line.strip(), 'after': replacement, 'reason': reason})
        return replacement + '\n' if replacement else ''


def optimize_stream(source, destination, *, max_seconds=180, max_output_bytes=None):
    optimizer = ZeroFactors()
    started, written = time.monotonic(), 0
    for number, line in enumerate(source, 1):
        if number % 10000 == 0:
            if time.monotonic() - started > max_seconds:
                raise TimeoutError('Bounded DQI text optimization exceeded its time budget.')
            if max_output_bytes is not None and written > max_output_bytes:
                raise OSError('Bounded DQI text optimization exceeded its disk budget.')
        rewritten = optimizer.rewrite(line, number)
        destination.write(rewritten)
        written += len(rewritten)
    return {
        'rewrites': dict(optimizer.changes),
        'rewrite_count': sum(optimizer.changes.values()),
        'examples': optimizer.examples,
        'opcodes': dict(optimizer.opcodes),
        'unsupported_examples': optimizer.unknown_examples,
        'output_bytes': written,
        'seconds': time.monotonic() - started
    }


def optimize_circuit_file(input_path: Path, output_path: Path) -> dict:
    import kickmix as km
    import tempfile
    with tempfile.NamedTemporaryFile('w+', suffix='.kmx', delete=False) as tmp_in, \
         tempfile.NamedTemporaryFile('w+', suffix='.kmx', delete=False) as tmp_out:
        tmp_in_path = Path(tmp_in.name)
        tmp_out_path = Path(tmp_out.name)

    try:
        c = km.Circuit.from_file(str(input_path))
        c.to_file(str(tmp_in_path), format='kmx')
        with open(tmp_in_path, 'r') as f_in, open(tmp_out_path, 'w') as f_out:
            report = optimize_stream(f_in, f_out)
        c_opt = km.Circuit.from_file(str(tmp_out_path), format='kmx')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        c_opt.to_file(str(output_path), format='kmb')
        stats = c_opt.operation_statistics()
        report['optimized_toffolis'] = stats.num_toffoli_like
        report['optimized_qubits'] = c_opt.num_qubits
        report['optimized_ops'] = len(c_opt)
        return report
    finally:
        tmp_in_path.unlink(missing_ok=True)
        tmp_out_path.unlink(missing_ok=True)
