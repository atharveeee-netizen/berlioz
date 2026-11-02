import re

lines = open('build/circuits/ehan_invsqrt.kmx', encoding='ascii').read().splitlines()
q_pat = re.compile(r'\bq(\d+)\b')

# We want to find a scratch wire for q61 between lines 3796 and 32150.
# What are all gates touching q61 between 3796 and 32150?
q61_lines = set(i for i in range(3796, 32151) if 'q61' in lines[i].split())
print(f"q61 has {len(q61_lines)} gates between 3796 and 32150.")

# For each candidate scratch qubit q in 22..60:
# Is q EVER used while q61 is live?
# Wait, when is q61 live?
# Does q61 have internal HMR resets between 3796 and 32150?
# Earlier we saw:
# Line 3796: R q61
# Line 23603: HMR q61 b481
# Line 23736: HMR q61 b0
# Line 23932: HMR q61 b0
# Line 24137: HMR q61 b423
# Line 31053: HMR q61 b308
# Line 31157: HMR q61 b0
# Line 31455: HMR q61 b0
# Line 31807: HMR q61 b0
# Line 32150: HMR q61 b0

# Let's list the distinct lifetime segments of q61:
q61_events = [3796, 23603, 23736, 23932, 24137, 31053, 31157, 31455, 31807, 32150]
segments = []
for idx in range(len(q61_events) - 1):
    start = q61_events[idx]
    end = q61_events[idx + 1]
    segments.append((start, end))

print(f"q61 has {len(segments)} independent lifetime segments:")
for idx, (s, e) in enumerate(segments):
    print(f"  Segment {idx}: lines {s} to {e} ({e - s} lines)")
