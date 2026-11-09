import sys
from pathlib import Path
import kickmix as km
import numpy as np

sys.modules['circ'] = km
sys.path.insert(0, 'verifiers')
sys.path.insert(0, 'build/somejoint_src/blocks/dqi/team-1028-narrow240/source/playbook/kit/decoder')

import importlib.util
HERE = Path('build/somejoint_src/blocks/dqi/team-1028-narrow240/source')

from dqi.verify_submission_dqi import ProblemSpecDQI, FieldTables, sample_shots, to_bits, optimal_dqi_weights
from final_decoder import synthesis as folds
from exp.decoder.common import ar
from exp.mul99.kernels import mul24_xor99

print("Folds functions:", [k for k in dir(folds) if not k.startswith('_')])
print("UG keys:", list(folds.ug.keys()))
print("SG keys:", list(folds.sg.keys()))

