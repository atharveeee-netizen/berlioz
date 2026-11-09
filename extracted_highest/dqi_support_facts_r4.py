"""Private R4 support-fact propagation; all control-scope boundaries stay barriers.

If q=1 implies c=1 on computational-basis support, diagonal phases and classical
bit operations preserve that implication. HMR can only shrink support on the
unmeasured qubits; invalidate the measured qubit and every reference to its old
version. Conditional HMR does not certify an unconditional reset. No branch
merging, decoder algebra, or frozen R3 module is changed.
"""

import collections
import re
import time

from dqi_zero_factors import ARITY, QUBIT, ZeroFactors, self_check as inherited_self_check

BIT = re.compile(r'b[0-9]+\Z')
CLASSICAL = {'REGISTER', 'APPEND_TO_REGISTER', 'BIT_STORE0', 'BIT_STORE1', 'BIT_INVERT'}


class SupportFacts(ZeroFactors):
    def __init__(self):
        super().__init__()
        self.preserved = collections.Counter()

    def rewrite(self, line, number):
        words = line.split()
        if not words:
            return line
        op, args = words[0], words[1:]
        if op in CLASSICAL:
            self.opcodes[op] += 1
            self.preserved[op] += 1
            return line
        if op in {'Z', 'CZ', 'CCZ'}:
            width = ARITY[op]
            qubits, suffix = args[:width], args[width:]
            valid = (len(qubits) == width and len(set(qubits)) == width
                     and all(QUBIT.fullmatch(q) for q in qubits))
            if valid and not suffix:
                self.preserved[op] += 1
                return super().rewrite(line, number)
            if valid and len(suffix) == 2 and suffix[0] == 'if' and BIT.fullmatch(suffix[1]):
                self.opcodes[op] += 1
                self.preserved[op] += 1
                return line
        if op == 'HMR':
            valid = len(args) in {2, 4} and QUBIT.fullmatch(args[0]) and BIT.fullmatch(args[1])
            conditional = len(args) == 4
            if conditional:
                valid = valid and args[2] == 'if' and BIT.fullmatch(args[3])
            if valid:
                self.opcodes[op] += 1
                self.preserved[op] += 1
                self.write(args[0], constant=None if conditional else 0)
                return line
        return super().rewrite(line, number)


def optimize_stream(source, destination, *, max_seconds=900, max_output_bytes=None):
    optimizer = SupportFacts()
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
            'preserved_operation_counts': dict(optimizer.preserved),
            'unsupported_examples': optimizer.unknown_examples,
            'output_bytes': written, 'seconds': time.monotonic() - started}


def self_check():
    """Compare complete tiny Kraus operators, including every HMR outcome/phase."""
    import io
    import itertools
    import numpy as np

    inherited = inherited_self_check()
    prefix = 'R q3\nR q4\nR q5\nCCX q0 q1 q3\n'
    programs = [prefix + phase + suffix + '\nCCX q3 q0 q5\n'
                for phase in ['Z q2', 'CZ q0 q2', 'CCZ q0 q1 q2']
                for suffix in ['', ' if b0']]
    programs += [
        prefix + 'REGISTER r0 "input"\nAPPEND_TO_REGISTER q0 r0\nBIT_STORE0 b0\nBIT_STORE1 b1\nBIT_INVERT b0 if b1\nCCX q3 q0 q5\n',
        prefix + 'CCX q1 q2 q4\nHMR q4 b2\nCZ q1 q2 if b2\nCCX q3 q0 q5\n',
        prefix + 'CCX q1 q2 q4\nHMR q4 b2 if b0\nCCX q3 q0 q5\n',
        prefix + 'HMR q0 b0\nCCX q3 q1 q5\n',
        prefix + 'HMR q0 b2 if b0\nCCX q3 q0 q5\nCCX q3 q1 q5\n',
        prefix + 'CCX q3 q2 q4\nHMR q3 b2 if b0\nCCX q4 q3 q5\nCCX q4 q0 q5\n',
        prefix + 'HMR q3 b2\nCCX q3 q2 q5\n',
        prefix + 'HMR q4 b2\nHMR q0 b3 if b2\nCCX q3 q1 q5\n',
        prefix + 'PUSH_CONDITION if b0\nZ q2\nPOP_CONDITION\nCCX q3 q0 q5\n',
        prefix + 'PUSH_CONDITION if b0\nX q0\nPOP_CONDITION\nCCX q3 q0 q5\n',
        prefix + 'H q2\nCCX q3 q0 q5\n',
        'R q3\nR q4\nR q5\nPUSH_CONDITION if b0\nCCX q0 q1 q3\nZ q2 if b1\nCCX q3 q0 q5\nPOP_CONDITION\n',
    ]

    def evaluate(program, initial, initial_bits, outcomes):
        vector, bits = initial.copy(), dict(initial_bits)
        stack, outcome_index = [], 0
        indices = np.arange(len(vector))
        for line in program.splitlines():
            words = line.split()
            if not words:
                continue
            op, args = words[0], words[1:]
            if op in {'REGISTER', 'APPEND_TO_REGISTER', 'INFO_TAG'}:
                continue
            if op == 'PUSH_CONDITION':
                assert args[0] == 'if' and len(args) == 2
                stack.append(bool(bits.get(args[1], 0)))
                continue
            if op == 'POP_CONDITION':
                stack.pop()
                continue
            enabled = all(stack)
            if 'if' in args:
                split = args.index('if')
                assert len(args[split:]) == 2
                enabled = enabled and bool(bits.get(args[split + 1], 0))
                args = args[:split]
            outcome = None
            if op == 'HMR':
                outcome = outcomes[outcome_index]
                outcome_index += 1
            if not enabled:
                continue
            if op in {'BIT_STORE0', 'BIT_STORE1', 'BIT_INVERT'}:
                assert len(args) == 1
                bits[args[0]] = (bits.get(args[0], 0) ^ 1) if op == 'BIT_INVERT' else int(op == 'BIT_STORE1')
                continue
            qubits = [int(q[1:]) for q in args if q.startswith('q')]
            if op == 'R':
                assert np.allclose(vector[(indices >> qubits[0]) & 1 == 1], 0)
            elif op in {'X', 'CX', 'CCX'}:
                mask = np.ones(len(vector), dtype=bool)
                for control in qubits[:-1]:
                    mask &= ((indices >> control) & 1).astype(bool)
                permutation = indices.copy()
                permutation[mask] ^= 1 << qubits[-1]
                vector = vector[permutation]
            elif op in {'Z', 'CZ', 'CCZ'}:
                mask = np.ones(len(vector), dtype=bool)
                for control in qubits:
                    mask &= ((indices >> control) & 1).astype(bool)
                vector[mask] *= -1
            elif op == 'HMR':
                target = qubits[0]
                low = indices[((indices >> target) & 1) == 0]
                high = low | (1 << target)
                result = np.zeros_like(vector)
                result[low] = (vector[low] + (-1) ** outcome * vector[high]) / np.sqrt(2)
                vector = result
                bits[args[1]] = outcome
            elif op == 'H':
                target = qubits[0]
                low = indices[((indices >> target) & 1) == 0]
                high = low | (1 << target)
                result = vector.copy()
                result[low] = (vector[low] + vector[high]) / np.sqrt(2)
                result[high] = (vector[low] - vector[high]) / np.sqrt(2)
                vector = result
            else:
                raise AssertionError(op)
        assert not stack
        return vector, bits

    states = []
    for basis in range(8):
        state = np.zeros(64, dtype=complex)
        state[basis] = 1
        states.append(state)
    for values in [np.arange(1, 9) * (1 + 1j * np.arange(8)), np.exp(1j * np.arange(8) ** 2)]:
        state = np.zeros(64, dtype=complex)
        state[:8] = values / np.linalg.norm(values)
        states.append(state)
    cases = rewrites = 0
    for program in programs:
        output = io.StringIO()
        audit = optimize_stream(io.StringIO(program), output)
        rewritten = output.getvalue()
        rewrites += audit['rewrite_count']
        measurements = sum(line.startswith('HMR ') for line in program.splitlines())
        for initial_bits in ({'b0': a, 'b1': b} for a, b in itertools.product(range(2), repeat=2)):
            for outcomes in itertools.product(range(2), repeat=measurements):
                for initial in states:
                    before, before_bits = evaluate(program, initial, initial_bits, outcomes)
                    after, after_bits = evaluate(rewritten, initial, initial_bits, outcomes)
                    assert np.allclose(before, after, atol=1e-12, rtol=1e-12), (program, rewritten, initial_bits, outcomes)
                    assert before_bits == after_bits
                    cases += 1
    for hmr in ['HMR q3 b2 if b0', 'HMR q0 b2 if b0']:
        optimizer = SupportFacts()
        for number, line in enumerate(prefix.splitlines() + [hmr], 1):
            optimizer.rewrite(line + '\n', number)
        assert optimizer.constants.get(hmr.split()[1]) is None
    for barrier in ['PUSH_CONDITION if b0', 'POP_CONDITION', 'H q2', 'HMR q3 b2 if unknown']:
        optimizer = SupportFacts()
        for number, line in enumerate(prefix.splitlines() + [barrier, 'CCX q3 q0 q5'], 1):
            last = optimizer.rewrite(line + '\n', number)
        assert last == 'CCX q3 q0 q5\n'
    assert rewrites >= 12
    return {'inherited': inherited, 'kraus_basis_and_phase_cases': cases,
            'programs': len(programs), 'safe_rewrites_exercised': rewrites,
            'measurement_outcomes': 'every branch, including conditional HMR',
            'scope_policy': 'PUSH/POP and unsupported operations remain full barriers'}


if __name__ == '__main__':
    print(self_check())