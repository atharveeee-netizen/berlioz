import sys
from pathlib import Path

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT / "build/somejoint_src/blocks/dqi/team-1028-narrow240/source"))
sys.path.insert(0, str(ROOT / "build/somejoint_src/blocks/dqi/team-1028-narrow240/source/exp/r-main/narrow240"))
sys.path.insert(0, str(ROOT / "build/somejoint_src/blocks/dqi/team-1028-narrow240/source/playbook/kit/decoder"))
sys.path.insert(0, str(ROOT / "build/somejoint_src/blocks/dqi/team-1028-narrow240/source/playbook/kit"))
sys.path.insert(0, str(ROOT / "verifiers"))

import kickmix as km

# Intercept alloc_qubits and free to track peak allocations by stage
class TracingBuilder:
    def __init__(self, raw):
        self.raw = raw
        self.live = 0
        self.peak = 0
        self.alloc_map = {}
        self.stage = "init"
        self.peak_by_stage = {}
        self.tags = {}

    def alloc_qubits(self, n):
        qs = self.raw.alloc_qubits(n)
        self.live += n
        if self.live > self.peak:
            self.peak = self.live
        cur_p = self.peak_by_stage.get(self.stage, 0)
        if self.live > cur_p:
            self.peak_by_stage[self.stage] = self.live
        for q in qs:
            self.alloc_map[q] = (self.stage, n)
        return qs

    def free(self, qs):
        try:
            n = len(qs)
        except TypeError:
            n = 1
        self.live -= n
        self.raw.free(qs)

    class _MarkCtx:
        def __init__(self, tracer, tag, raw_ctx):
            self.tracer = tracer
            self.tag = tag
            self.raw_ctx = raw_ctx
            self.prev = tracer.stage
        def __enter__(self):
            self.tracer.stage = self.tag
            return self.raw_ctx.__enter__()
        def __exit__(self, *args):
            self.tracer.stage = self.prev
            return self.raw_ctx.__exit__(*args)

    def mark(self, tag):
        return self._MarkCtx(self, tag, self.raw.mark(tag))

    def __getattr__(self, name):
        if hasattr(self.raw, name):
            return getattr(self.raw, name)
        return getattr(km, name)

raw = km.CircuitBuilder()
tracer = TracingBuilder(raw)
sys.modules['circ'] = tracer

import importlib.util
spec = importlib.util.spec_from_file_location('decode_retimed', 'build/somejoint_src/blocks/dqi/team-1028-narrow240/source/exp/r-main/narrow240/decode_retimed.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

tracer.stage = "alloc_ports"
S = [tracer.alloc_qubits(12) for _ in range(70)]
E = [raw.alloc_bits(12) for _ in range(4095)]

print(f"Initial syndrome ports: {tracer.live} qubits (840 expected)")

# Run decode
mod.decode(tracer, S, E)

print(f"\nOverall peak live qubits: {tracer.peak}")
print("Peak by stage:", tracer.peak_by_stage)
