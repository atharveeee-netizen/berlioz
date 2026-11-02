import numpy as np
import kickmix as km

field = km.GF2Field(12)

# Verify key equation on random syndromes and errors
# In Goppa/BCH codes:
# Given locators X_1 .. X_k (distinct nonzero field elements, k <= 35)
# and error values Y_1 .. Y_k
# Syndromes S_i = sum_{l=1}^k Y_l * X_l^(i+1) for i = 0..69
# Lambda(x) = prod_{l=1}^k (1 - X_l * x)
# Omega(x) = sum_{l=1}^k Y_l * X_l * prod_{j != l} (1 - X_j * x)

# Let's test with k = 3 errors:
rng = np.random.default_rng(42)
k = 3
locs = rng.choice(range(1, 4095), size=k, replace=False).tolist()
vals = rng.choice(range(1, 4095), size=k, replace=False).tolist()

# Compute S_0 .. S_69:
S = []
for i in range(70):
    val = 0
    for l in range(k):
        # Y_l * X_l^(i+1)
        term = vals[l]
        for _ in range(i + 1):
            term = field.mul(term, locs[l])
        val = field.add(val, term)
    S.append(val)

# Compute Lambda polynomial:
# start with P = [1]
Lam = [1]
for x in locs:
    # multiply Lam by (1 - x*t) = (1 + x*t) in GF(2)
    new_Lam = [0] * (len(Lam) + 1)
    for idx, c in enumerate(Lam):
        new_Lam[idx] = field.add(new_Lam[idx], c)
        new_Lam[idx + 1] = field.add(new_Lam[idx + 1], field.mul(c, x))
    Lam = new_Lam

print(f"Degree of Lambda: {len(Lam) - 1} (expected {k})")

# Compute Omega polynomial: Omega(x) = S(x) * Lambda(x) mod x^k
# Omega_i = sum_{j=0}^i S_{i-j} * Lam_j
Omega = []
for i in range(k):
    val = 0
    for j in range(i + 1):
        if j < len(Lam):
            val = field.add(val, field.mul(S[i - j], Lam[j]))
    Omega.append(val)

print(f"Omega: {Omega}")

# NOW TEST RECOVERY OF S FROM LAMBDA AND OMEGA VIA RECURRENCE:
# S_recovered[0] = Omega[0] (since Lam[0] = 1)
# S_recovered[i] = Omega[i] ^ sum_{j=1}^k Lam[j] * S_recovered[i-j] (for i < k)
# S_recovered[i] = sum_{j=1}^k Lam[j] * S_recovered[i-j] (for i >= k)

S_rec = []
for i in range(70):
    val = Omega[i] if i < len(Omega) else 0
    for j in range(1, len(Lam)):
        if i - j >= 0:
            val = field.add(val, field.mul(Lam[j], S_rec[i - j]))
    S_rec.append(val)

match = (S == S_rec)
print(f"All 70 syndromes recovered perfectly: {match}")
if not match:
    for i in range(70):
        if S[i] != S_rec[i]:
            print(f"  Mismatch at {i}: original {S[i]}, recovered {S_rec[i]}")
else:
    print("SUCCESS! The Newton LFSR recurrence holds exactly over all 70 syndromes!")
