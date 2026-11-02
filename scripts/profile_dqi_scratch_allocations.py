"""Profile DQI scratch qubit allocations across the retimed decoder pipeline.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import kickmix as km

HERE = Path("build/somejoint_src/blocks/dqi/team-1028-narrow240/source").resolve()
sys.modules['circ'] = km

spec = importlib.util.spec_from_file_location('decoder_under_test', HERE / 'exp/r-main/narrow240/decode_retimed.py')
module = importlib.util.module_from_spec(spec)
sys.modules['decoder_under_test'] = module
spec.loader.exec_module(module)

# Intercept alloc_qubits and free to track peak usage
class InstrumentBuilder:
    def __init__(self):
        self.builder = km.CircuitBuilder()
        self.current_alloc = 0
        self.peak_alloc = 0
        self.history = []

    def alloc_qubits(self, count):
        q = self.builder.alloc_qubits(count)
        self.current_alloc += count
        if self.current_alloc > self.peak_alloc:
            self.peak_alloc = self.current_alloc
        self.history.append(('alloc', count, self.current_alloc))
        return q

    def free(self, q):
        count = len(q) if hasattr(q, '__len__') else 1
        self.builder.free(q)
        self.current_alloc -= count
        self.history.append(('free', count, self.current_alloc))

    def __getattr__(self, name):
        return getattr(self.builder, name)

b = km.CircuitBuilder()
S = [b.alloc_qubits(12) for _ in range(70)]
E = [b.alloc_bits(12) for _ in range(4095)]

print(f"[+] Base syndrome qubits allocated: {70 * 12} qubits")
module.decode(b, S, E)

c = b.finish_circuit()
stats = c.operation_statistics()
print(f"[+] Total circuit qubits: {c.num_qubits}")
print(f"[+] Scratch qubits used:  {c.num_qubits - 840}")
print(f"[+] Toffoli gates:        {stats.num_toffoli_like}")
print(f"[+] Total operations:     {len(c)}")
