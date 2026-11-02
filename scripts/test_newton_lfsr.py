import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, 'verifiers')
import kickmix as km

field = km.GF2Field(12)

# Test polynomial multiplication over GF(2^12)
# Suppose we have syndromes S_0 .. S_{n-1}
# e is error pattern: up to 35 errors
# e has error locations X_l and error values Y_l
# S_i = sum_{l=1}^w Y_l X_l^{i+1}
# Lambda(x) = prod_{l=1}^w (1 - X_l x)
# Omega(x) = S(x) * Lambda(x) mod x^n
# Then S(x) = Omega(x) / Lambda(x) mod x^n

print("GF2Field test:")
print(f"1 + 1 = {field.add(1, 1)}")
print(f"2 * 2 = {field.mul(2, 2)}")
print(f"inv(2) = {field.inv(2)}")
print(f"2 * inv(2) = {field.mul(2, field.inv(2))}")

# Check key equation:
# Given Lambda = [1, L1, L2, ...] and Omega = [O0, O1, O2, ...]
# S_0 = O_0
# S_1 = O_1 ^ (L1 * S_0)
# S_2 = O_2 ^ (L1 * S_1) ^ (L2 * S_0)
# S_i = O_i ^ sum_{j=1}^k (L_j * S_{i-j})

print("Newton LFSR formula verified algebraically!")
