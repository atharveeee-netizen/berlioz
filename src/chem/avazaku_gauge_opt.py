"""Full-Rank Riemannian SO(60) Manifold & Exact Pair Polish Gauge Optimizer
Directly reduces LCU 1-norm on DF-THC without changing physical Hamiltonian, e1, e2, or E_gap.
Grounded in avazaku C60 gauge descent solution.
"""
import argparse
import os
import sys
import time
import numpy as np

def objective(a):
    return float(np.sum(np.sum(np.abs(a), axis=-2)**2))

def smooth_value_gradient(a, epsilon):
    u = np.sqrt(a * a + epsilon * epsilon)
    sums = u.sum(axis=-2, keepdims=True)
    return float(np.sum(sums * sums)), 2 * sums * a / u

def cayley_step(a, epsilon, initial_step=.1):
    _, gradient = smooth_value_gradient(a, epsilon)
    raw = a.T @ gradient
    skew = .5 * (raw - raw.T)
    norm = float(np.linalg.norm(skew))
    if norm < 1e-15:
        return a.copy(), 0., 0
    skew /= norm
    eye = np.eye(a.shape[-1])
    old = objective(a)
    for backtrack in range(16):
        step = initial_step * .5**backtrack
        q = np.linalg.solve(eye + .5 * step * skew, eye - .5 * step * skew)
        candidate = a @ q
        gain = old - objective(candidate)
        if gain > max(1e-13, old * 1e-14):
            return candidate, gain, backtrack + 1
    return a.copy(), 0., 16

def best_pair(x, y):
    halfpi = np.pi / 2
    roots = np.mod(np.concatenate([np.arctan2(-x, y), np.arctan2(y, x)]), np.pi)
    edges = np.unique(np.concatenate([[0., halfpi], roots[(roots > 1e-13) & (roots < halfpi - 1e-13)]]))
    mid = (edges[:-1] + edges[1:]) / 2
    c = np.cos(mid)[:, None]
    s = np.sin(mid)[:, None]
    sx = np.sign(c * x + s * y)
    sy = np.sign(-s * x + c * y)
    ax = sx @ x; ay = sx @ y; bx = sy @ x; by = sy @ y
    aa = ax * ax + by * by; bb = ay * ay + bx * bx; cc = ax * ay - bx * by
    theta = np.mod(.5 * (np.arctan2(2 * cc, aa - bb) + np.pi), np.pi)
    interior = theta[(theta > edges[:-1] + 1e-13) & (theta < edges[1:] - 1e-13)]
    trial = np.concatenate([edges, interior])
    c = np.cos(trial)[:, None]
    s = np.sin(trial)[:, None]
    nx = c * x + s * y
    ny = -s * x + c * y
    values = np.abs(nx).sum(axis=1)**2 + np.abs(ny).sum(axis=1)**2
    j = int(np.argmin(values))
    old = float(np.abs(x).sum()**2 + np.abs(y).sum()**2)
    if values[j] >= old - max(1e-14, old * 2e-15):
        return x.copy(), y.copy(), 0.
    return nx[j], ny[j], old - float(values[j])

def pair_descent(a, seconds, seed=281060):
    out = a.copy()
    start = time.monotonic()
    rng = np.random.default_rng(seed)
    groups, _, rank = out.shape
    pairs = [(i, j) for i in range(rank) for j in range(i + 1, rank)]
    trials = accepted = 0
    while time.monotonic() - start < seconds:
        group = int(rng.integers(groups))
        i, j = pairs[int(rng.integers(len(pairs)))]
        out[group, :, i], out[group, :, j], gain = best_pair(out[group, :, i], out[group, :, j])
        trials += 1
        accepted += gain > 0
    return out

def manifold_descent(a, seconds, seed=281061):
    out = a.copy()
    start = time.monotonic()
    rng = np.random.default_rng(seed)
    groups, _, rank = out.shape
    scales = np.sqrt(np.mean(a * a, axis=(1, 2)))
    trials = accepted = pair_trials = pair_accepted = 0
    while time.monotonic() - start < seconds:
        group = int(rng.integers(groups))
        epsilon = float(scales[group] * (1e-2, 1e-3, 1e-4, 1e-5)[(trials // groups) % 4])
        new, gain, _ = cayley_step(out[group], epsilon, initial_step=(.1, .03, .01)[trials % 3])
        trials += 1
        if gain > 0:
            out[group] = new
            accepted += 1
        for _ in range(24):
            if time.monotonic() - start >= seconds:
                break
            i, j = sorted(map(int, rng.choice(rank, 2, replace=False)))
            out[group, :, i], out[group, :, j], gain = best_pair(out[group, :, i], out[group, :, j])
            pair_trials += 1
            pair_accepted += gain > 0
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("out")
    ap.add_argument("--seconds", type=float, default=60.0)
    args = ap.parse_args()

    z = np.load(args.inp, allow_pickle=False)
    data = {k: np.array(z[k]) for k in z.files}
    w, h = data["W"], data["H2_I"]
    a = np.concatenate([w, h[:, None, :]], axis=1)
    g0 = a @ a.swapaxes(1, 2)
    c0 = objective(a)
    print(f"[*] Starting C60 Riemannian manifold gauge descent: initial loss = {c0:.4f}")

    half_sec = args.seconds / 2.0
    warm = pair_descent(a, half_sec, seed=281060)
    c_warm = objective(warm)
    print(f"[*] Warm start complete ({half_sec:.1f}s): loss = {c_warm:.4f} (gain: {c0 - c_warm:.4f})")

    manifold = manifold_descent(warm, half_sec, seed=281061)
    c_mani = objective(manifold)
    print(f"[*] Manifold complete ({half_sec:.1f}s): loss = {c_mani:.4f} (total gain: {c0 - c_mani:.4f})")

    drift = float(np.max(np.abs(manifold @ manifold.swapaxes(1, 2) - g0)))
    print(f"[*] Max Gram drift: {drift:.2e} (tolerance < 1e-8: {drift < 1e-8})")
    assert drift < 1e-8, f"Gram drift exceeded tolerance: {drift}"

    data["W"] = manifold[:, :-1, :]
    data["H2_I"] = manifold[:, -1, :]
    np.savez(args.out, **data)
    print(f"[+] Successfully saved optimized factorization to {args.out}")

if __name__ == "__main__":
    main()
