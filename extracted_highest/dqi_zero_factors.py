"""Conservative semantic rewrites of official KMX text, never binary patches.

Inspiration: Kirill Tymchishin's public exact control-absorption rewrite
(https://www.kaggle.com/code/kirilltym/quantum-circuits-qrom-tower42).
This implementation independently propagates certified zero-factor facts.
Unsupported instructions are barriers: they discard all accumulated facts.
"""
import collections
import re
import time

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
        self.versions.clear(); self.factors.clear(); self.constants.clear()

    def valid(self, factors):
        return {item for item in factors if self.versions[item[0]] == item[1]}

    def get(self, q):
        return self.valid(self.factors.get(q, set())) | {(q, self.versions[q])}

    def write(self, q, factors=(), constant=None):
        self.versions[q] += 1
        # Dropping a certified factor is safe; bound propagation memory.
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
                    remaining.remove(q); changed = True
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

    def rewrite(self, line, number):
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
            q = args[0]; old = self.constants.get(q)
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
                    # Z on a certified |1> reproduces the required global phase.
                    replacement = 'Z ' + args[0]
                else:
                    replacement = ('Z' if len(simple) == 1 else 'CZ') + ' ' + ' '.join(simple)
                reason = 'zero or implied phase control'
        elif op == 'SWAP':
            a, b = args
            fa, fb = self.get(a), self.get(b)
            ca, cb = self.constants.get(a), self.constants.get(b)
            self.versions[a] += 1; self.versions[b] += 1
            self.factors[a], self.factors[b] = self.valid(fb), self.valid(fa)
            self.constants.pop(a, None); self.constants.pop(b, None)
            if cb is not None: self.constants[a] = cb
            if ca is not None: self.constants[b] = ca
        elif op == 'CSWAP':
            control, a, b = args
            ca, cb, cc = self.constants.get(a), self.constants.get(b), self.constants.get(control)
            both_masked = ((control, self.versions[control]) in self.get(a)
                           and (control, self.versions[control]) in self.get(b))
            if cc == 0 or ca == cb == 0:
                replacement = ''; reason = 'inactive Fredkin swap'
                # Exact identity: the operand facts remain unchanged.
            else:
                fa, fb = self.get(a), self.get(b)
                if cc == 1 or both_masked:
                    replacement = 'SWAP ' + a + ' ' + b; reason = 'implied Fredkin control'
                shared = fa & fb
                self.versions[a] += 1; self.versions[b] += 1
                self.factors[a] = self.valid(fb if cc == 1 or both_masked else shared)
                self.factors[b] = self.valid(fa if cc == 1 or both_masked else shared)
                self.constants.pop(a, None); self.constants.pop(b, None)
                if cc == 1 or both_masked:
                    if cb is not None: self.constants[a] = cb
                    if ca is not None: self.constants[b] = ca
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
    return {'rewrites': dict(optimizer.changes), 'rewrite_count': sum(optimizer.changes.values()),
            'examples': optimizer.examples, 'opcodes': dict(optimizer.opcodes),
            'unsupported_examples': optimizer.unknown_examples,
            'output_bytes': written, 'seconds': time.monotonic() - started}


def self_check():
    """Exhaustive basis/phase equivalence of seeded and adversarial small programs."""
    import io
    import itertools
    import random

    def evaluate(program, value, n):
        bits = [(value >> i) & 1 for i in range(n)]
        phase = 0
        for line in program.splitlines():
            words = line.split()
            if not words or words[0] in {'INFO_TAG', 'BARRIER'}: continue
            op = words[0]; q = [int(a[1:]) for a in words[1:]]
            if op == 'R': bits[q[0]] = 0
            elif op == 'X': bits[q[0]] ^= 1
            elif op == 'CX': bits[q[1]] ^= bits[q[0]]
            elif op == 'CCX': bits[q[2]] ^= bits[q[0]] & bits[q[1]]
            elif op == 'Z': phase ^= bits[q[0]]
            elif op == 'CZ': phase ^= bits[q[0]] & bits[q[1]]
            elif op == 'CCZ': phase ^= bits[q[0]] & bits[q[1]] & bits[q[2]]
            elif op == 'SWAP': bits[q[0]], bits[q[1]] = bits[q[1]], bits[q[0]]
            elif op == 'CSWAP':
                if bits[q[0]]: bits[q[1]], bits[q[2]] = bits[q[2]], bits[q[1]]
            else: raise AssertionError(op)
        return tuple(bits), phase

    programs = [
        'R q2\nCCX q0 q1 q2\nCCX q2 q0 q3\n',
        'R q2\nCCX q0 q1 q2\nX q0\nCCX q2 q0 q3\n',
        'R q2\nR q3\nCCX q0 q1 q2\nCX q2 q3\nCCZ q2 q3 q4\n',
        'R q2\nCCX q0 q1 q2\nBARRIER\nCCX q2 q0 q3\n',
        'R q2\nR q3\nCCX q0 q1 q2\nCX q2 q3\nCSWAP q0 q2 q3\n',
    ]
    rng = random.Random(20261023)
    for _ in range(220):
        lines = ['R q4', 'R q5', 'CCX q0 q1 q4', 'CX q4 q5']
        for _ in range(70):
            op = rng.choice(list(ARITY) + ['BARRIER'])
            args = [] if op == 'BARRIER' else rng.sample(range(6), ARITY[op])
            lines.append(op + ' ' + ' '.join('q' + str(i) for i in args))
        programs.append('\n'.join(lines) + '\n')
    cases, rewrites = 0, 0
    for program in programs:
        out = io.StringIO()
        audit = optimize_stream(io.StringIO(program), out)
        rewrites += audit['rewrite_count']
        for value in range(64):
            assert evaluate(program, value, 6) == evaluate(out.getvalue(), value, 6), (program, out.getvalue(), value)
            cases += 1
    assert rewrites > 100
    # A new control context is an unsupported-instruction barrier.
    opt = ZeroFactors()
    for number, line in enumerate(['R q2\n', 'CCX q0 q1 q2\n', 'PUSH_CONDITION b0\n', 'CCX q2 q0 q3\n'], 1):
        output = opt.rewrite(line, number)
    assert output == 'CCX q2 q0 q3\n'
    return {'basis_phase_cases': cases, 'programs': len(programs), 'safe_rewrites_exercised': rewrites}


if __name__ == '__main__':
    print(self_check())