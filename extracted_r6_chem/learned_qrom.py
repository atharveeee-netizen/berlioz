"""Exact signed-Givens four-address ANGLE XOR compiler for learned factors.

SPDX-License-Identifier: Apache-2.0

Attribution: signed-angle gauge and four-address decomposition originate in
Kozykorpesh / kozykappa V3, run361677445:
https://www.kaggle.com/code/kozykappa/quantum-ai-lb-score-6-68108?scriptVersionId=361677445
The split-ANF MBU eraser follows our banked_angles_v3, with the credited
Sumit Chongder -> Kozykorpesh -> Kirill Tym -> anazemcev lineage:
https://www.kaggle.com/code/sumitchongder/notebook2f196e646b?scriptVersionId=361357149

This adaptation supports arbitrary legal address counts, beta8/beta10 and
batch widths that fit128Q. Prefix tables receive an explicit polynomial
extension, used identically for loading and erasure. All target registers
may be dirty. Only private scratch/bank registers must start clean.
"""
from __future__ import annotations

from functools import lru_cache
from math import ceil

import numpy as np


def batch_deltas(words, J=3):
    words = np.asarray(words, dtype=np.int64)
    if words.ndim != 2 or J < 1:
        raise ValueError("Expected a2D angle table and positive J")
    padded = np.zeros((len(words), ceil(words.shape[1] / J) * J), dtype=np.int64)
    padded[:, :words.shape[1]] = words
    batches = padded.reshape(len(words), -1, J).transpose(1, 0, 2)
    delta = batches.copy()
    delta[1:] ^= batches[:-1]
    return delta


def mobius_transform(table):
    result = list(map(int, table))
    if not result or len(result) & (len(result) - 1):
        raise ValueError("ANF table size must be a power of two")
    for bit in range((len(result) - 1).bit_length()):
        step = 1 << bit
        for start in range(0, len(result), 2 * step):
            for offset in range(step):
                result[start + step + offset] ^= result[start + offset]
    return result


def xor_and(builder, left, right, targets):
    """XOR one product into any number of arbitrary dirty target wires."""
    targets = list(targets)
    if not targets:
        return
    first = targets[0]
    for target in targets[1:]:
        builder.cx(first, target)
    builder.ccx(left, right, first)
    for target in reversed(targets[1:]):
        builder.cx(first, target)


def pebbled_init(builder, table, address, outputs, scratch):
    """XOR a prefix lookup plus its explicit ANF extension into outputs."""
    import kickmix as km
    address, outputs, scratch = map(list, (address, outputs, scratch))
    H, n = len(table), len(address)
    if not 1 <= H <= (1 << n):
        raise ValueError("Prefix length exceeds high-address register")
    coefficients = mobius_transform(list(table) + [0] * ((1 << n) - H))
    coefficients[H:] = [0] * ((1 << n) - H)
    completed = mobius_transform(coefficients)
    if completed[:H] != list(table):
        raise AssertionError("Prefix ANF extension changed a legal value")
    stats = dict(monomial_ands=0, recomputed_ands=0, pebble_sites=0,
                 direct_leaf_ands=0, scratch=len(scratch), high_addresses=H,
                 high_address_bits=n)

    @lru_cache(None)
    def children(mask, last):
        return tuple((mask | (1 << j), j) for j in range(last + 1, n)
                     if (mask | (1 << j)) < H)

    @lru_cache(None)
    def need(mask, last):
        return max([1 + need(c, j) for c, j in children(mask, last)
                    if children(c, j)] + [0])

    def targets(mask):
        return [outputs[j] for j in range(len(outputs))
                if (coefficients[mask] >> j) & 1]

    def walk(mask, last, control, path, free):
        erased = []
        # Degree4 pebble is the exact earlier own improvement. Erase only
        # ancestors; the current product control remains valid and allocated.
        if mask.bit_count() >= 4 and need(mask, last) > len(free):
            count = need(mask, last) - len(free)
            # A complete power-of-two prefix may need a deeper pebble than
            # degree4. Postpone until enough ancestors are available; never
            # erase the parent of the current retained control prematurely.
            if 0 < count <= len(path) - 1:
                erased = path[:count]
                for a, c, t in reversed(erased):
                    builder.del_and(a, c, t)
                    free.append(t)
                stats["pebble_sites"] += 1
        ts = targets(mask)
        if ts:
            if control is None:
                builder.x(km.array(ts))
            else:
                builder.cx(control, km.array(ts))
        for child, j in children(mask, last):
            if not mask:
                walk(child, j, address[j], path, free)
            elif not children(child, j):
                ts = targets(child)
                if ts:
                    xor_and(builder, control, address[j], ts)
                    stats["direct_leaf_ands"] += 1
            else:
                if not free:
                    raise ValueError("Batch exceeds the128Q pebble workspace budget")
                target = free.pop()
                builder.init_and(control, address[j], target)
                stats["monomial_ands"] += 1
                walk(child, j, target, path + [(control, address[j], target)], free)
                builder.del_and(control, address[j], target)
                free.append(target)
        for a, c, t in erased:
            free.remove(t)
            builder.init_and(a, c, t)
            stats["recomputed_ands"] += 1

    walk(0, -1, None, [], scratch.copy())
    return completed, stats


def erase_anf(builder, *, table, address, target, low_bits=None):
    """Exact HMR/ANF phase correction, including all extension addresses."""
    import kickmix as km
    address, target = list(address), list(target)
    n = len(address)
    if n < 2 or len(table) != (1 << n):
        raise ValueError("ANF erasure needs a complete table with at least2 bits")
    low_bits = n // 2 if low_bits is None else int(low_bits)
    if not 0 < low_bits < n:
        raise ValueError("Both ANF halves must be nonempty")
    if any(value < 0 or value >= (1 << len(target)) for value in table):
        raise ValueError("ANF value exceeds bank width")
    coefficients = mobius_transform(table)
    measurements = builder.alloc_bits(len(target))
    builder.hmr(km.array(target), measurements)
    parity = builder.alloc_bits(1)[0]
    low_count, high_bits = 1 << low_bits, n - low_bits
    retained = [mask for mask in range(1, low_count) if mask.bit_count() > 1]
    scratch_count = len(retained) + high_bits - 1
    extra = builder.alloc_qubits(max(0, scratch_count - len(target)))
    scratch = target + list(extra)
    low = {1 << bit: address[bit] for bit in range(low_bits)}
    for mask, qubit in zip(retained, scratch):
        bit = mask.bit_length() - 1
        builder.init_and(low[mask ^ (1 << bit)], address[bit], qubit)
        low[mask] = qubit
    carries = scratch[len(retained):scratch_count]

    def correct(high_mask, high_qubit):
        for low_mask in range(low_count):
            coefficient = coefficients[low_mask | (high_mask << low_bits)]
            if not coefficient:
                continue
            builder.bit_store(parity, False)
            while coefficient:
                bit = (coefficient & -coefficient).bit_length() - 1
                builder.cx(measurements[bit], parity)
                coefficient &= coefficient - 1
            if not low_mask and not high_mask:
                builder.neg_if(parity)
                continue
            builder.push_condition(parity)
            if not low_mask:
                builder.z(high_qubit)
            elif not high_mask:
                builder.z(low[low_mask])
            else:
                builder.cz(low[low_mask], high_qubit)
            builder.pop_condition()

    def walk(mask, last, control):
        correct(mask, control)
        for bit in range(last + 1, high_bits):
            child_mask = mask | (1 << bit)
            if not mask:
                walk(child_mask, bit, address[low_bits + bit])
            else:
                child = carries[mask.bit_count() - 1]
                builder.init_and(control, address[low_bits + bit], child)
                walk(child_mask, bit, child)
                builder.del_and(control, address[low_bits + bit], child)

    walk(0, -1, None)
    for mask in reversed(retained):
        bit = mask.bit_length() - 1
        builder.del_and(low[mask ^ (1 << bit)], address[bit], low[mask])
    builder.free(extra)
    return dict(address_bits=n, low_bits=low_bits, high_bits=high_bits,
                anf_toffoli=(1 << low_bits) - low_bits - 1 + (1 << high_bits) - high_bits - 1,
                scratch_count=scratch_count, anf_table_identity="PASS")


def fourbank_tables(delta, brot):
    delta = np.asarray(delta)
    if brot not in (8, 9, 10, 11, 12) or delta.ndim != 2 or not np.issubdtype(delta.dtype, np.integer):
        raise ValueError("Expected integer2D table with beta8,9 or10")
    if np.any(delta < 0) or np.any(delta >= (1 << brot)):
        raise ValueError("Angle word outside requested beta")
    if np.any(((delta >> (brot - 1)) ^ (delta >> (brot - 2))) & 1):
        raise ValueError("Signed gauge bit(beta-1)=bit(beta-2) is required")
    A, J = delta.shape
    if A < 9 or J < 1:
        raise ValueError("Fourbank compiler requires at least9 legal addresses")
    n, W, BW = (A - 1).bit_length(), brot * J, (brot - 1) * J
    padded = np.zeros((ceil(A / 4) * 4, J), dtype=np.int64)
    padded[:A] = delta
    packed = [sum(int(v) << (j * brot) for j, v in enumerate(row)) for row in padded]
    mask = (1 << (brot - 1)) - 1

    def compact(value):
        return sum(((value >> (j * brot)) & mask) << (j * (brot - 1)) for j in range(J))

    def expand(value):
        return sum((((value >> (j * (brot - 1))) & mask) |
                    (((value >> (j * (brot - 1) + brot - 2)) & 1) << (brot - 1))) << (j * brot)
                   for j in range(J))

    values, restored = [], []
    for h in range(len(packed) // 4):
        v0, v1, v2, v3 = packed[4 * h:4 * h + 4]
        d1, d2, d3 = map(compact, (v0 ^ v1, v0 ^ v2, v0 ^ v1 ^ v2 ^ v3))
        values.append(v0 | (d1 << W) | (d2 << (W + BW)) | (d3 << (W + 2 * BW)))
        for a in range(4):
            d = (d1 if a & 1 else 0) ^ (d2 if a & 2 else 0) ^ (d3 if a == 3 else 0)
            restored.append(v0 ^ expand(d))
    if restored != packed:
        raise AssertionError("All-row fourbank integer certificate failed")
    return values, dict(addresses=A, padded_addresses=len(packed), selection_bits=n,
                        J=J, brot=brot, target_width=W, bank_width=3 * BW,
                        all_row_integer_identity="PASS")


def build(delta, brot=10, *, return_report=False, scratch_count=None):
    import kickmix as km
    values, report = fourbank_tables(delta, brot)
    n, J, W = report["selection_bits"], report["J"], report["target_width"]
    BW = (brot - 1) * J
    available = 128 - n - W - 3 * BW
    preferred = max(6, n - 4)
    scratch_count = min(preferred, max(0, available)) if scratch_count is None else int(scratch_count)
    if scratch_count < 1 or scratch_count > available:
        raise ValueError("Batch width cannot fit the128Q cap")
    b = km.CircuitBuilder()
    sel = b.create_quantum_register(n, "selection")
    target = [q for j in range(J) for q in b.create_quantum_register(brot, f"word_{j}")]
    bank = list(b.alloc_qubits(3 * BW))
    scratch = b.alloc_qubits(scratch_count)
    completed, init = pebbled_init(b, values, sel[2:], target + bank, scratch)
    b.free(scratch)
    both = b.alloc_qubits(1)[0]
    b.init_and(sel[0], sel[1], both)
    for s, control in enumerate((sel[0], sel[1], both)):
        for j in range(J):
            for bit in range(brot - 1):
                targets = [target[j * brot + bit]]
                if bit == brot - 2:
                    targets.append(target[j * brot + brot - 1])
                xor_and(b, control, bank[s * BW + j * (brot - 1) + bit], targets)
    b.del_and(sel[0], sel[1], both)
    b.free(both)
    cleanup = erase_anf(b, table=[value >> W for value in completed],
                        address=sel[2:], target=bank)
    b.free(km.array(bank))
    circuit = b.finish_circuit()
    if circuit.num_qubits > 128:
        raise AssertionError("Compiled circuit exceeds128Q")
    report.update(num_qubits=int(circuit.num_qubits),
                  static_toffoli=int(circuit.operation_statistics().num_toffoli_like),
                  init=init, cleanup=cleanup, dirty_target_contract="XOR unchanged input plus delta")
    return (circuit, report) if return_report else circuit