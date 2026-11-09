import re
import kickmix as km

lines = open('build/circuits/ehan_invsqrt.kmx', encoding='ascii').read().splitlines()
q_pat = re.compile(r'\bq(\d+)\b')

# 1. Trace exact lifetime segments of every scratch qubit q >= 22.
# A scratch qubit must be in |0> at the start of a segment and returned to |0> at the end.
# In Kickmix:
# Reset is done by 'R q' or 'HMR q b' (which resets q to |0>).
# Let's inspect all HMR and R operations.

segments = []
current_start = {}
last_op = {}

for line_idx, line in enumerate(lines):
    parts = line.strip().split()
    if not parts:
        continue
    op = parts[0]
    qubits_in_line = [int(m.group(1)) for m in q_pat.finditer(line)]
    
    if op in ('HMR', 'R'):
        q = int(parts[1][1:])
        if q >= 22:
            start = current_start.get(q, line_idx)
            segments.append((q, start, line_idx))
            if q in current_start:
                del current_start[q]
            if q in last_op:
                del last_op[q]
    else:
        for q in qubits_in_line:
            if q >= 22:
                if q not in current_start:
                    current_start[q] = line_idx
                last_op[q] = line_idx

for q, start in current_start.items():
    end = last_op.get(q, len(lines) - 1)
    segments.append((q, start, end))

print(f"Total segments: {len(segments)}")

# Sort segments by start line
segments.sort(key=lambda x: (x[1], x[2]))

# Interval graph coloring (greedy first-fit)
# For each segment, find the lowest available color (qubit index >= 22)
# that is not currently in use by any overlapping segment.
free_colors = []
active_segments = [] # list of (end_line, color)
seg_colors = {} # (orig_q, start, end) -> assigned_color

max_color_used = 21

for orig_q, start, end in segments:
    # Expire finished segments
    active_segments.sort(key=lambda x: x[0])
    still_active = []
    for finish, col in active_segments:
        if finish < start:
            # col is now free
            free_colors.append(col)
        else:
            still_active.append((finish, col))
    active_segments = still_active
    
    # Pick lowest available color
    if free_colors:
        free_colors.sort()
        assigned = free_colors.pop(0)
    else:
        max_color_used += 1
        assigned = max_color_used
        
    active_segments.append((end, assigned))
    seg_colors[(orig_q, start, end)] = assigned

print(f"Max color used: {max_color_used}")
print(f"Total qubits required with optimal interval coloring: {max_color_used + 1}")

