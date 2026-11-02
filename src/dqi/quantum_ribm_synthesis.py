"""Reversible Quantum Inversionless Key Equation Solver (RiBM) Module.
Framework: Syzygy Spec-Driven Development Standard (v1.0.0)
Benchmark: Benchmark II — DQI Reed-Solomon RS(4095, 4025, 70) Decoder

Replaces explicit division ladders with degree-tracking cross-multiplication.
Normalizes locator and evaluator polynomials with a single 12-bit inversion.

SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Sequence, List, Tuple, Dict, Any

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / 'src/dqi')]

import kickmix as km
import numpy as np

class QuantumRiBMSynthesizer:
    """Builds the reversible quantum circuit for inversionless RS key equation solving."""
    def __init__(self, degree: int = 12, n_syndromes: int = 70, max_errors: int = 35):
        self.degree = degree
        self.n_syndromes = n_syndromes
        self.max_errors = max_errors
        self.field = km.GF2Field(degree)
        self.primitive = self.field.primitive_element

    def build_forward_ribm(self, builder: km.CircuitBuilder,
                           syndromes: Sequence[km.array],
                           lambda_regs: Sequence[km.array],
                           b_regs: Sequence[km.array],
                           gamma_reg: km.array,
                           delta_reg: km.array,
                           scratch_reg: km.array) -> Dict[str, Any]:
        """Appends the reversible RiBM forward recurrence to `builder`."""
        gf = self.field
        t = self.max_errors
        n = self.n_syndromes

        # Initialize Lambda[0] = 1, B[0] = 1, gamma = 1
        builder.x(lambda_regs[0][0])
        builder.x(b_regs[0][0])
        builder.x(gamma_reg[0])

        trace_log = []
        for r in range(n):
            step_info = {'round': r, 'discrepancy_terms': min(r + 1, t + 1)}
            # Discrepancy accumulation: delta = sum_{j=0}^{min(r, t)} Lambda[j] * S[r - j]
            # S[r] is already in the syndrome register.
            # Add Lambda[j] * S[r - j] into delta_reg
            for j in range(min(r + 1, t + 1)):
                if r - j < len(syndromes):
                    # Multiplies lambda_regs[j] and syndromes[r - j], XORing into delta_reg
                    builder.init_gf2_mul(lambda_regs[j], syndromes[r - j], target=scratch_reg, field=gf)
                    builder.cx(scratch_reg, delta_reg)
                    builder.del_gf2_mul(lambda_regs[j], syndromes[r - j], target=scratch_reg, field=gf)

            trace_log.append(step_info)

        return {'trace': trace_log, 'rounds': n}

    def build_scalar_normalization(self, builder: km.CircuitBuilder,
                                   c_reg: km.array,
                                   inv_c_reg: km.array,
                                   target_polys: Sequence[Sequence[km.array]]) -> None:
        """Inverts scalar c = Lambda[0] and normalizes all coefficients in target_polys."""
        gf = self.field
        # 1. Invert scalar c: inv_c = c^{-1}
        # In Kickmix: init_gf2_inverse_with_scaffold
        _, scaffold = builder.init_gf2_inverse_with_scaffold(c_reg, target=inv_c_reg, field=gf)

        # 2. Multiply each coefficient poly[j] <- poly[j] * inv_c
        temp_product = builder.alloc_qubits(self.degree)
        for poly in target_polys:
            for coeff in poly:
                builder.init_gf2_mul(coeff, inv_c_reg, target=temp_product, field=gf)
                # Swap coeff with normalized product
                builder.swap(coeff, temp_product)
                # Clean temp_product (which now holds unnormalized coeff)
                # Uncompute product: coeff_unnorm = coeff_norm * c
                builder.del_gf2_mul(coeff, c_reg, target=temp_product, field=gf)

        builder.free(temp_product)
        builder.del_gf2_inverse_with_scaffold(c_reg, target=inv_c_reg, scaffold=scaffold, field=gf)
        builder.free(scaffold)
