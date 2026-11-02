import kickmix as km

# Test remapping q61 -> q47 for lines >= 37000:
# At line 36868: HMR q47 b0. q47 is reset to |0> and unused until end.
# At line 32150: HMR q61 b0. q61 is reset to |0>.
# From line 43749 to 47248: q61 is used.
# If we replace q61 with q47 in all instructions after line 37000:
# What happens?

lines = open('build/circuits/ehan_invsqrt.kmx', encoding='ascii').read().splitlines()

new_lines = []
for i, l in enumerate(lines):
    if i >= 37000:
        # replace q61 with q47 as whole word
        parts = l.split()
        new_parts = []
        for p in parts:
            if p == 'q61':
                new_parts.append('q47')
            else:
                new_parts.append(p)
        new_lines.append(' '.join(new_parts))
    else:
        new_lines.append(l)

out_kmx = 'build/circuits/test_remap_q61_q47.kmx'
open(out_kmx, 'w', encoding='ascii').write('\n'.join(new_lines) + '\n')
print(f"Wrote {out_kmx}. Testing with verifier on max-x 16...")

