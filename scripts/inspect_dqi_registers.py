import sys
from pathlib import Path
sys.path.insert(0, 'verifiers')
import kickmix as km

HERE = Path('build/somejoint_src/blocks/dqi/team-1028-narrow240/source')
sys.modules['circ'] = km
sys.path[:0] = [str(HERE), str(HERE / 'exp/r-main/narrow240'), str(HERE / 'playbook/kit/decoder'), str(HERE / 'playbook/kit')]

from final_decoder import decode as ref

print("Inspecting geometry and registers in ref:")
print("Groups count:", len(ref.groups))
print("qs count:", len(ref.qs))
print("cs count:", len(ref.cs))
print("ks count:", len(ref.ks))
print("matrix shape:", len(ref.matrix), "x", len(ref.matrix[0]) if ref.matrix else 0)
