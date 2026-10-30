import numpy as np
import kickmix as km

field = km.GF2Field(12)
alpha = field.primitive_element
n_syndromes = 70
max_errors = 35

def compute_syndromes(error_positions, error_values):
    syndromes = [0] * n_syndromes
    for i in range(n_syndromes):
        s = 0
        for pos, val in zip(error_positions, error_values):
            p = field.pow(alpha, (i + 1) * pos)
            prod = field.mul(val, p)
            s ^= prod
        syndromes[i] = s
    return syndromes

def ribm(syndromes):
    # RiBM algorithm:
    # Lambda = 1, B = 1, gamma = 1, k = 0
    # Polynomials represented as lists of coefficients [c0, c1, c2, ...]
    Lambda = [1] + [0] * max_errors
    B = [1] + [0] * max_errors
    gamma = 1
    k = 0

    for r in range(len(syndromes)):
        # Compute discrepancy: delta = sum_{j=0}^r Lambda[j] * S[r - j]
        delta = 0
        for j in range(len(Lambda)):
            if Lambda[j] != 0 and (r - j) >= 0:
                delta ^= field.mul(Lambda[j], syndromes[r - j])

        # Next Lambda: Lambda_{new} = gamma * Lambda + delta * x * B
        Lambda_new = [0] * (max_errors + 1)
        for i in range(max_errors + 1):
            t1 = field.mul(gamma, Lambda[i]) if Lambda[i] != 0 else 0
            t2 = 0
            if i > 0 and B[i - 1] != 0 and delta != 0:
                t2 = field.mul(delta, B[i - 1])
            Lambda_new[i] = t1 ^ t2

        if delta != 0 and k >= 0:
            B = list(Lambda)
            gamma = delta
            k = -k - 1
        else:
            # B = x * B
            B = [0] + B[:-1]
            k = k + 1

        Lambda = Lambda_new

    # Trim trailing zeros
    deg = max_errors
    while deg > 0 and Lambda[deg] == 0:
        deg -= 1
    return Lambda[:deg + 1]

# Test single error
pos = [42]
val = [123]
S = compute_syndromes(pos, val)
Lambda = ribm(S)
print("Single error Lambda:", Lambda)
root = field.pow(alpha, (4095 - pos[0]) % 4095)
val_at_root = 0
x_pow = 1
for coeff in Lambda:
    val_at_root ^= field.mul(coeff, x_pow)
    x_pow = field.mul(x_pow, root)
print("Single error val_at_root:", val_at_root)

# Test multiple errors
rng = np.random.default_rng(20261030)
for num_err in [2, 5, 10, 20, 35]:
    positions = rng.choice(4095, size=num_err, replace=False).tolist()
    values = rng.integers(1, 4096, size=num_err).tolist()
    S = compute_syndromes(positions, values)
    Lambda = ribm(S)
    print(f"Num err: {num_err}, Lambda deg: {len(Lambda)-1}")
    for p in positions:
        x = field.pow(alpha, (4095 - p) % 4095)
        res = 0
        x_pow = 1
        for coeff in Lambda:
            res ^= field.mul(coeff, x_pow)
            x_pow = field.mul(x_pow, x)
        assert res == 0, f"Error at pos {p} was not a root!"
print("[+] All RiBM tests passed successfully!")
