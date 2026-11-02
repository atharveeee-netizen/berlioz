import math

# Baseline references:
COST_REF_INVSQRT = 2076775.0
COST_REF_DQI = 24439739777574.605
COST_REF_CHEM = 3355598687.0

# Known chemistry frontier costs:
# v34 / isabe11a: lambda_eff ~ 47.0372 -> cost = 326801702.15 (R_chem = 10.26800)
# r8 champion: cost = 337925828.60 (R_chem = 9.92998)
# Isabe11a v49: cost = 326815726.71 (R_chem = 10.26755)
CHEM_R_CANDIDATES = [10.26800, 10.26755, 9.93000]

# Known invsqrt costs and qubit counts:
# 63Q: 89194 (23.284x) - error bound tight
# 62Q Ehan: 100568.50 (20.65034x)
# 62Q yoyobar: 100692.58 (20.62489x)
# 61Q compacted: ~98950 (20.988x)
# 58Q compacted: ~94076 (22.075x)
# 55Q compacted: ~89210 (23.279x)
INVSQRT_R_CANDIDATES = [20.65034, 20.62489, 20.98800, 22.07500, 23.27900]

# DQI known qubit counts:
# Q in {892, 889, 881, 876}
# Rep factor: 1.2 (for 0 errors)
# Base ref cost: 24.4397e12

TOP10 = [
    (1, "Breaking1800", 27.99617, 20),
    (2, "Jack", 27.39302, 29),
    (3, "Simulation", 27.32155, 11),
    (4, "Schrödinger's cat lived", 27.06470, 43),
    (5, "Thinking...", 26.81091, 39),
    (6, "Bingran You", 26.80320, 35),
    (7, "James & Tony", 26.65597, 43),
    (8, "Adisak Sukul", 26.35447, 52),
    (9, "trust the transpiler", 26.15339, 36),
    (10, "????????", 26.11915, 41),
]

print("=== REVERSE-ENGINEERING TOP 10 LEADERBOARD CONFIGURATIONS ===\n")

for rank, team, score, subs in TOP10:
    target_prod = score ** 3
    print(f"--- Rank #{rank}: {team} | Score: {score:.5f} | Product: {target_prod:.1f} (Subs: {subs}) ---")
    
    best_diff = 1e9
    best_config = None
    
    for r_chem in CHEM_R_CANDIDATES:
        for r_inv in INVSQRT_R_CANDIDATES:
            r_dqi = target_prod / (r_chem * r_inv)
            dqi_cost = COST_REF_DQI / r_dqi
            
            # For each candidate qubit count Q in {892, 889, 876}:
            for Q in [892, 889, 881, 876]:
                # Cost = 1.2 * Q^2 * Toffolis
                toffolis = dqi_cost / (1.2 * (Q ** 2))
                
                # Check if toffolis is physically plausible:
                # Baseline SomeJoint is ~403k, BusyaPrime is ~400k.
                # Bypassing unsynthesis (-172k) -> ~228k
                # Bypassing unsynthesis + unextract (-369k) -> ~120k - 220k
                if 100000 <= toffolis <= 450000:
                    diff = abs((r_chem * r_inv * r_dqi) ** (1/3) - score)
                    print(f"  [Q={Q}] Toffolis/shot={toffolis:,.1f} | R_dqi={r_dqi:.2f}x | R_inv={r_inv:.2f}x | R_chem={r_chem:.2f}x")
