import re

lines = open('build/circuits/ehan_invsqrt.kmx', encoding='ascii').read().splitlines()

q_pattern = re.compile(r'\bq(\d+)\b')

# For each qubit, find all intervals where it is 'live'
# A qubit is live from when it is initialized (or line 0 if it's an input q0..q21) 
# until it is reset/uncomputed (HMR or final gate)
first_seen = {}
last_seen = {}

for i, l in enumerate(lines):
    qubits = [int(m.group(1)) for m in q_pattern.finditer(l)]
    for q in qubits:
        if q not in first_seen:
            first_seen[q] = i
        last_seen[q] = i

# Let's check reset points (R qX) and measurement points (HMR qX)
resets = {q: [] for q in range(62)}
hmrs = {q: [] for q in range(62)}

for i, l in enumerate(lines):
    parts = l.strip().split()
    if not parts:
        continue
    if parts[0] == 'R':
        q = int(parts[1][1:])
        resets[q].append(i)
    elif parts[0] == 'HMR':
        q = int(parts[1][1:])
        hmrs[q].append(i)

print("=== QUBIT LIFETIME PROFILE ===")
for q in range(62):
    r_pts = resets[q]
    h_pts = hmrs[q]
    if r_pts or h_pts:
        print(f"q{q:2d}: Resets at {r_pts}, HMRs at {h_pts}")

# Calculate concurrency:
# At each gate i, which qubits are currently in use?
# If a qubit has 'R', it becomes live at R. If it has 'HMR', it stops being live after HMR!
# If it has neither, it is live from first_seen[q] to last_seen[q].
live_at = [0] * len(lines)
for i in range(len(lines)):
    active = 0
    for q in range(62):
        # determine if q is live at line i
        f = first_seen[q]
        l = last_seen[q]
        if f <= i <= l:
            # check if it's before first reset (for scratch qubits)
            if resets[q] and i < resets[q][0]:
                continue
            # check if it's after last HMR
            if hmrs[q] and i > hmrs[q][-1]:
                continue
            active += 1
    live_at[i] = active

max_live = max(live_at)
max_idx = live_at.index(max_live)
print(f"\nMax concurrently active qubits: {max_live} at gate {max_idx}")
