import sys
import time
from pathlib import Path
import numpy as np
import torch

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT / "src/chem"))
sys.path.insert(0, str(ROOT / "verifiers"))

import dft_eval as de
from qat import Problem, decode, dev, DT, N

# Load the champion factor
inp_path = ROOT / "build/ml30_apex_optimum/dfthcsos/submission.npz"
z = np.load(inp_path)
params = {k: np.array(z[k]) for k in z.files}
edges = params["tree_edges"].astype(np.int64)
w0, Wo0 = de.native(params)
R, B, C = w0.shape
print(f"Loaded factor: R={R}, B={B}, C={C}")

P = Problem(edges)
Tp = P.Tp.to(DT)
cw = P.cw.to(DT)
il0, il1 = P.il_t

# 1. Evaluate baseline at brot=8
th_cont = de.tree_angles(params["U"].reshape(-1, N), edges)
words_8 = de.to_words(th_cont, 8)
v2_8 = decode(torch.tensor(words_8, dtype=DT, device=dev) / 128.0, P.edges).reshape(R, B, N)
M_8 = (v2_8[:, :, il0] * v2_8[:, :, il1]) * cw
A_8 = torch.einsum("rbc,rbp->rcp", torch.tensor(w0, dtype=DT, device=dev), M_8).reshape(R * C, -1)
e2_8 = torch.linalg.norm(A_8.T @ A_8 - Tp).item()
print(f"Baseline brot=8 e2: {e2_8*1000:.3f} mHa")

# 2. Now round to brot=7
words_7 = de.to_words(th_cont, 7)
v2_7 = decode(torch.tensor(words_7, dtype=DT, device=dev) / 64.0, P.edges).reshape(R, B, N)
M_7 = (v2_7[:, :, il0] * v2_7[:, :, il1]) * cw
A_7_raw = torch.einsum("rbc,rbp->rcp", torch.tensor(w0, dtype=DT, device=dev), M_7).reshape(R * C, -1)
e2_7_raw = torch.linalg.norm(A_7_raw.T @ A_7_raw - Tp).item()
print(f"Raw brot=7 e2 (before w refit): {e2_7_raw*1000:.3f} mHa")

# 3. Optimize w to minimize e2 for these exact 7-bit vectors!
w_opt = torch.tensor(w0, dtype=DT, device=dev, requires_grad=True)
optimizer = torch.optim.LBFGS([w_opt], lr=1.0, max_iter=20, history_size=50, line_search_fn="strong_wolfe")

def closure():
    optimizer.zero_grad()
    A = torch.einsum("rbc,rbp->rcp", w_opt, M_7).reshape(R * C, -1)
    loss = torch.linalg.norm(A.T @ A - Tp)
    loss.backward()
    return loss

t0 = time.time()
print("\nRefitting weights w on 7-bit vectors with L-BFGS...")
for it in range(15):
    optimizer.step(closure)
    with torch.no_grad():
        A = torch.einsum("rbc,rbp->rcp", w_opt, M_7).reshape(R * C, -1)
        cur_e2 = torch.linalg.norm(A.T @ A - Tp).item()
    print(f"  Iter {it:2d}: e2 = {cur_e2*1000:7.3f} mHa ({time.time()-t0:.1f}s)")
    if cur_e2 <= 0.020:
        print("  --> PASSED ACCURACY GATE e2 <= 20 mHa!")
        break
