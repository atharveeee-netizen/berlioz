#!/usr/bin/env python3
"""Verification of Forney error value equivalence under RiBM.
SPDX-License-Identifier: Apache-2.0
"""
import random, sys
sys.path.insert(0, '.')
import kickmix as km

gf = km.GF2Field(12)
alpha = gf.primitive_element

from tools.verify_inplace_ribm_scan import compute_syndromes, solve_std_bm, solve_ribm, find_roots

def compute_omega(syndromes, Lambda, max_len=70):
    # Omega(x) = S(x) * Lambda(x) mod x^{2t}
    omega = [0] * max_len
    for i in range(len(syndromes)):
        for j in range(len(Lambda)):
            if i + j < max_len:
                omega[i + j] ^= gf.mul(syndromes[i], Lambda[j])
    # trim trailing zeros
    deg = len(omega) - 1
    while deg > 0 and omega[deg] == 0:
        deg -= 1
    return omega[:deg + 1]

def eval_poly(poly, x):
    val = 0
    px = 1
    for coeff in poly:
        val ^= gf.mul(coeff, px)
        px = gf.mul(px, x)
    return val

def formal_derivative(poly):
    # In GF(2^12), derivative of x^{2k} is 0, derivative of x^{2k+1} is x^{2k}
    deriv = []
    for i in range(1, len(poly), 2):
        deriv.extend([poly[i], 0])
    while deriv and deriv[-1] == 0:
        deriv.pop()
    return deriv if deriv else [0]

def forney_eval(roots, Lambda, Omega):
    error_values = []
    lam_prime = formal_derivative(Lambda)
    for p in roots:
        X = gf.pow(alpha, -p)
        # Forney formula: e_j = X^2 * Omega(X) / Lambda'(X)
        X2 = gf.mul(X, X)
        num = gf.mul(X2, eval_poly(Omega, X))
        den = eval_poly(lam_prime, X)
        assert den != 0, f"Lambda'(X) is zero at root position {p}"
        val = gf.div(num, den)
        error_values.append(val)
    return error_values

def test_forney():
    print("[*] Testing Forney error evaluation equivalence across 50 random trials...")
    random.seed(20261102)
    for trial in range(50):
        w = random.randint(1, 35)
        pos = sorted(random.sample(range(4095), w))
        vals = [random.randint(1, 4095) for _ in range(w)]
        syn = compute_syndromes(pos, vals)
        
        lam_std = solve_std_bm(syn)
        lam_ribm = solve_ribm(syn)
        
        omega_std = compute_omega(syn, lam_std)
        omega_ribm = compute_omega(syn, lam_ribm)
        
        roots_std = find_roots(lam_std)
        roots_ribm = find_roots(lam_ribm)
        assert roots_std == pos
        assert roots_ribm == pos
        
        vals_std = forney_eval(roots_std, lam_std, omega_std)
        vals_ribm = forney_eval(roots_ribm, lam_ribm, omega_ribm)
        
        assert vals_std == vals, f"Trial {trial}: Standard Forney failed to recover injected values!"
        assert vals_ribm == vals, f"Trial {trial}: RiBM Forney failed to recover injected values!"
        assert vals_ribm == vals_std, f"Trial {trial}: RiBM values != Standard values!"
        
    print("[+] All 50 trials passed bit-exact Forney error value recovery!")

if __name__ == '__main__':
    test_forney()
