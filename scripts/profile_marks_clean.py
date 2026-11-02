import sys, time
from pathlib import Path
import kickmix as km
sys.modules['circ'] = km

sys.path.insert(0, 'build/somejoint_src/blocks/dqi/team-1028-narrow240/source/playbook/kit/decoder')
import importlib.util
HERE = Path('build/somejoint_src/blocks/dqi/team-1028-narrow240/source')

import decode as baseline
baseline.scan = lambda b, A, B, E, **kwargs: None

spec = importlib.util.spec_from_file_location('decoder_under_test', HERE / 'exp/r-main/narrow240/decode_retimed.py')
module = importlib.util.module_from_spec(spec)
sys.modules['decoder_under_test'] = module
spec.loader.exec_module(module)

stages = [
    'mask_projection',
    'initial',
    'extract',
    'synthesis',
    'convert',
    'unconvert',
    'unsynthesis',
    'unextract',
    'uninitial',
    'restore_masks'
]

def run_up_to(stage_idx):
    b = km.CircuitBuilder()
    S = [b.alloc_qubits(12) for _ in range(70)]
    E = [b.alloc_bits(12) for _ in range(4095)]
    
    if stage_idx >= 0:
        mt = module.ref.baseline.project(b, S, E)
    if stage_idx >= 1:
        module.ref.linear_words(b, S, module.ref.matrix)
    if stage_idx >= 2:
        et = module.extraction(b, S)
    if stage_idx >= 3:
        A, B, undo = module.synthesize(b, S, et['pole'])
    if stage_idx >= 4:
        ct = module.convert_safe(b, A, B, monic_root=True)
    if stage_idx >= 5:
        module.convert_safe(b, A, B, True, phase_token=ct)
    if stage_idx >= 6:
        undo()
    if stage_idx >= 7:
        module.extraction(b, S, True, et)
    if stage_idx >= 8:
        module.ref.linear_words(b, S, module.ref.matrix, True)
    if stage_idx >= 9:
        module.ref.baseline.restore(b, E, mt)
        
    c = b.finish_circuit()
    return c.operation_statistics().num_toffoli_like

prev = 0
print("\n=== STAGE-BY-STAGE TOFFOLI PROFILING ===")
for idx, name in enumerate(stages):
    cum = run_up_to(idx)
    diff = cum - prev
    print(f"{name:20s}: {diff:7d} Toffolis (cumulative: {cum:7d})")
    prev = cum

