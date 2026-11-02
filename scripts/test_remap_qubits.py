"""Test if scratch qubits in invsqrt.kmx can be colored into <= 36 physical scratch wires (total <= 58 qubits)."""

import re

lines = open('build/circuits/ehan_invsqrt.kmx', encoding='ascii').read().splitlines()
q_pattern = re.compile(r'\bq(\d+)\b')

intervals = [] # list of (qubit, start_line, end_line)
current_segment_start = {}

for line_idx, line in enumerate(lines):
    parts = line.strip().split()
    if not parts:
        continue
    op = parts[0]
    qubits = [int(m.group(1)) for m in q_pattern.finditer(line)]
    
    if op == 'R':
        q = int(parts[1][1:])
        if q >= 22:
            if q in current_segment_start:
                intervals.append((q, current_segment_start[q], line_idx - 1))
            current_segment_start[q] = line_idx
    elif op == 'HMR':
        q = int(parts[1][1:])
        if q >= 22:
            start = current_segment_start.get(q, 0)
            intervals.append((q, start, line_idx))
            if q in current_segment_start:
                del current_segment_start[q]
    else:
        for q in qubits:
            if q >= 22:
                if q not in current_segment_start:
                    current_segment_start[q] = line_idx

for q, start in current_segment_start.items():
    intervals.append((q, start, len(lines) - 1))

print(f"Total active lifetime segments extracted: {len(intervals)}")

# Sort intervals by start_line
intervals.sort(key=lambda x: (x[1], x[2]))

# Standard First-Fit Linear Scan
active_allocations = []
interval_to_color = {}
max_colors_used = 0

for idx, (orig_q, start, end) in enumerate(intervals):
    # Free any allocations whose end_line < start
    active_allocations = [a for a in active_allocations if a[1] >= start]
    used_colors = {a[0] for a in active_allocations}
    
    # Always pick lowest available color >= 22
    c = 22
    while c in used_colors:
        c += 1
    assigned_color = c
        
    active_allocations.append((assigned_color, end))
    interval_to_color[(orig_q, start, end)] = assigned_color
    if assigned_color > max_colors_used:
        max_colors_used = assigned_color

print(f"Maximum physical qubit color assigned with Pure First-Fit: q{max_colors_used}")
print(f"Total physical qubits required: {max_colors_used + 1}")
if max_colors_used < 58:
    print(f"SUCCESS! Pure First-Fit fits in {max_colors_used + 1} qubits (<= 58Q)!")
else:
    print(f"Peak color {max_colors_used} >= 58.")
    # Check when peak color occurs:
    # Find which gate line has max concurrent active intervals
