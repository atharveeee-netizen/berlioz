import sys
from pathlib import Path
import traceback

HERE = Path(".").resolve()
sys.path.insert(0, str(HERE / "build/somejoint_src/blocks/dqi/team-1028-narrow240/source"))
sys.path.insert(0, str(HERE / "build/somejoint_src/blocks/dqi/team-1028-narrow240/source/exp/r-main/narrow240"))
sys.path.insert(0, str(HERE / "build/somejoint_src/blocks/dqi/team-1028-narrow240/source/playbook/kit/decoder"))
sys.path.insert(0, str(HERE / "build/somejoint_src/blocks/dqi/team-1028-narrow240/source/playbook/kit"))

import kickmix as km
sys.modules['circ'] = km

import importlib.util
spec = importlib.util.spec_from_file_location('decoder_under_test', HERE / 'build/somejoint_src/blocks/dqi/team-1028-narrow240/source/exp/r-main/narrow240/decode_retimed.py')
module = importlib.util.module_from_spec(spec)
sys.modules['decoder_under_test'] = module
spec.loader.exec_module(module)

class TrackingBuilder:
    def __init__(self, raw):
        self._raw = raw
        self.live = 0
        self.peak = 0
        self.peak_stack = None
        self.peak_stage = "init"
        self.current_stage = "init"
        self.stage_peaks = {}

    def alloc_qubits(self, n):
        qs = self._raw.alloc_qubits(n)
        self.live += n
        if self.live > self.stage_peaks.get(self.current_stage, 0):
            self.stage_peaks[self.current_stage] = self.live
        if self.live > self.peak:
            self.peak = self.live
            self.peak_stage = self.current_stage
            stack = traceback.extract_stack()
            self.peak_stack = [f"{s.filename.split('/')[-1].split(chr(92))[-1]}:{s.lineno} in {s.name}" for s in stack[-6:-1]]
        return qs

    def free(self, qs):
        try:
            n = len(qs)
        except TypeError:
            n = 1
        self.live -= n
        self._raw.free(qs)

    class _Ctx:
        def __init__(self, tb, tag, raw_ctx):
            self.tb = tb
            self.tag = tag
            self.raw_ctx = raw_ctx
            self.prev = tb.current_stage
        def __enter__(self):
            self.tb.current_stage = self.tag
            return self.raw_ctx.__enter__()
        def __exit__(self, *args):
            self.tb.current_stage = self.prev
            return self.raw_ctx.__exit__(*args)

    def mark(self, tag):
        return self._Ctx(self, tag, self._raw.mark(tag))

    def __getattr__(self, name):
        return getattr(self._raw, name)

raw = km.CircuitBuilder()
b = TrackingBuilder(raw)
S = [b.alloc_qubits(12) for _ in range(70)]
E = [raw.alloc_bits(12) for _ in range(4095)]
print(f"Allocated ports: {b.live} qubits", flush=True)

module.decode(b, S, E)

print(f"\nDecoding complete!", flush=True)
print(f"Overall Peak: {b.peak} qubits", flush=True)
print(f"Peak Stage: {b.peak_stage}", flush=True)
print("Peak Stack:")
for line in b.peak_stack:
    print("  ", line)
print("\nPeaks by stage:")
for stage, count in b.stage_peaks.items():
    print(f"  {stage:20s}: {count}")
