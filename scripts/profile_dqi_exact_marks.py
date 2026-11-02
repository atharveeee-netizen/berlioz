"""Profile exact Toffoli count in each section of the DQI decoder by intercepting marks."""

from contextlib import contextmanager
import importlib.util
from pathlib import Path
import sys
import kickmix as km

HERE = Path('build/somejoint_src/blocks/dqi/team-1028-narrow240/source')
sys.modules['circ'] = km
sys.path[:0] = [str(HERE), str(HERE / 'exp/r-main/narrow240')]

# Load decode_retimed
spec = importlib.util.spec_from_file_location('decoder_under_test', HERE / 'exp/r-main/narrow240/decode_retimed.py')
module = importlib.util.module_from_spec(spec)
sys.modules['decoder_under_test'] = module
spec.loader.exec_module(module)

# Wrap CircuitBuilder to track gate additions per mark
class InstrumentedBuilder:
    def __init__(self, builder):
        self._b = builder
        self.section_toffolis = {}
        self.section_ops = {}
        self.current_section = "top_level"

    def __getattr__(self, name):
        attr = getattr(self._b, name)
        # Intercept Toffoli-like gate methods
        if name in ('ccx', 'ccz', 'cswap'):
            def wrapper(*args, **kwargs):
                self.section_toffolis[self.current_section] = self.section_toffolis.get(self.current_section, 0) + 1
                self.section_ops[self.current_section] = self.section_ops.get(self.current_section, 0) + 1
                return attr(*args, **kwargs)
            return wrapper
        elif callable(attr):
            def wrapper(*args, **kwargs):
                self.section_ops[self.current_section] = self.section_ops.get(self.current_section, 0) + 1
                return attr(*args, **kwargs)
            return wrapper
        return attr

    @contextmanager
    def mark(self, name):
        prev = self.current_section
        self.current_section = name
        with self._b.mark(name):
            yield
        self.current_section = prev

raw_b = km.CircuitBuilder()
ib = InstrumentedBuilder(raw_b)

S = [ib.alloc_qubits(12) for _ in range(70)]
E = [ib.alloc_bits(12) for _ in range(4095)]

print("[*] Running decode with instrumentation...")
module.decode(ib, S, E)

print("\n=== EXACT TOFFOLI GATES BY MARKED SECTION ===")
total_toff = 0
for sec, toff in ib.section_toffolis.items():
    ops = ib.section_ops.get(sec, 0)
    print(f"{sec:20s}: Toffolis = {toff:7d}  (Total ops = {ops:8d})")
    total_toff += toff
print("-" * 50)
print(f"{'TOTAL':20s}: Toffolis = {total_toff:7d}")
