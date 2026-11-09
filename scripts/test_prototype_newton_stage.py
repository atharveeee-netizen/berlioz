import sys, time
from pathlib import Path
import kickmix as km
import numpy as np

sys.modules['circ'] = km
sys.path.insert(0, 'verifiers')
sys.path.insert(0, 'build/somejoint_src/blocks/dqi/team-1028-narrow240/source/playbook/kit/decoder')

import importlib.util
HERE = Path('build/somejoint_src/blocks/dqi/team-1028-narrow240/source')

from dqi.verify_submission_dqi import ProblemSpecDQI, FieldTables, sample_shots, to_bits, optimal_dqi_weights
from exp.decoder.common import ar
from exp.mul99.kernels import mul24_xor99

spec = ProblemSpecDQI.benchmark_instance()
tables = FieldTables(km.GF2Field(spec.degree))
rng = np.random.default_rng(12345)
weight_probs = optimal_dqi_weights(spec.m, spec.max_errors, spec.degree, spec.r) ** 2

num_shots = 2
syndromes, mbuc, phases = sample_shots(spec, tables, rng, num_shots, weight_probs)

print("[*] Loading modules...", flush=True)
spec_mod = importlib.util.spec_from_file_location('decoder_under_test', HERE / 'exp/r-main/narrow240/decode_retimed.py')
module = importlib.util.module_from_spec(spec_mod)
sys.modules['decoder_under_test'] = module
spec_mod.loader.exec_module(module)

print("[*] Module loaded successfully!", flush=True)

