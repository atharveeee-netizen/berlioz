"""Reformulated Inversionless Berlekamp-Massey (RiBM) Key Equation Solver over GF(2^12).

Evidence Level: CLASSICAL_PROTOTYPE
Implements the inversionless key equation solver for (4095, 70, 12) Reed-Solomon codes.
Eliminates finite field inversions from the locator polynomial computation, replacing
them with degree-tracking cross-multiplications by discrepancy gamma.

NOTE: This is a classical prototype. Full end-to-end quantum reversible synthesis
requires reversible registers for B(x) and Lambda(x) updates, Chien search root finding,
and Forney evaluator integration. The production DQI circuit uses the verified Proos-Zalka
extended Euclidean decoder with selective quadratic-phase erasure.

SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
import kickmix as km

class RiBMSolver:
    """Classical RiBM implementation over GF(2^b)."""
    def __init__(self, degree: int = 12, max_errors: int = 35):
        self.degree = degree
        self.field = km.GF2Field(degree)
        self.max_errors = max_errors

    def solve_locator(self, syndromes: list[int] | tuple[int, ...]) -> list[int]:
        """Finds the error locator polynomial Lambda(x) from syndrome sequence without field division."""
        gf = self.field
        t = self.max_errors
        Lambda = [1] + [0] * t
        B = [1] + [0] * t
        gamma = 1
        k = 0

        for r in range(len(syndromes)):
            delta = 0
            for j in range(len(Lambda)):
                if Lambda[j] != 0 and (r - j) >= 0:
                    delta ^= gf.mul(Lambda[j], syndromes[r - j])

            Lambda_new = [0] * (t + 1)
            for i in range(t + 1):
                t1 = gf.mul(gamma, Lambda[i]) if Lambda[i] != 0 else 0
                t2 = 0
                if i > 0 and B[i - 1] != 0 and delta != 0:
                    t2 = gf.mul(delta, B[i - 1])
                Lambda_new[i] = t1 ^ t2

            if delta != 0 and k >= 0:
                B = list(Lambda)
                gamma = delta
                k = -k - 1
            else:
                B = [0] + B[:-1]
                k = k + 1

            Lambda = Lambda_new

        deg = t
        while deg > 0 and Lambda[deg] == 0:
            deg -= 1
        return Lambda[:deg + 1]
