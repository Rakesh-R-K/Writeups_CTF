from pathlib import Path
import math

p = Path('c:/Users/Rakesh R K/Downloads/bitsctf/radio_telescope/rt7-log.txt')
lines = [l.strip() for l in p.read_text().splitlines() if l.strip()]
nums = [float(l) for l in lines]

# Try several heuristics to find hidden message
# 1) fractional parts * 100 -> integers
fracs = [abs(n - math.floor(n)) for n in nums]
fracs100 = [int(round(f*100)) for f in fracs]

# 2) fractional parts * 1000
fracs1000 = [int(round(f*1000)) for f in fracs]

# 3) look for runs of nearly-constant values (oscillations)

print('Total lines', len(nums))
print('Sample nums[:20]:', nums[:20])
print('\nMost common fractional*100 values:')
from collections import Counter
print(Counter(fracs100).most_common(30))
print('\nMost common fractional*1000 values:')
print(Counter(fracs1000).most_common(30))

# Try to interpret small integers (fracs100) as ASCII where plausible
cand = ''.join(chr(x) for x in fracs100 if 32 <= x < 127)
print('\nASCII from frac*100 filtered printable (first 200):')
print(cand[:200])

# Another heuristic: take integer part mod 256
ints_mod = [int(abs(n)) % 256 for n in nums]
print('\nFirst 100 ints_mod:', ints_mod[:100])
print('\nLook for long runs of small-range numbers (possible encoded blocks):')

# Find clusters where difference between consecutive is small
clusters = []
cur = [nums[0]]
for x,y in zip(nums, nums[1:]):
    if abs(y-x) < 1.0: cur.append(y)
    else:
        if len(cur) > 8: clusters.append(cur)
        cur=[y]
if len(cur)>8: clusters.append(cur)
print('Found', len(clusters), 'clusters (len>8). Sizes:', [len(c) for c in clusters[:10]])

# Print first cluster sample
if clusters:
    print('\nFirst cluster sample (first 50):')
    print(clusters[0][:50])

# Heuristic: in clusters, take each value rounded to nearest integer and map to ASCII if in range
for i, c in enumerate(clusters[:5]):
    arr = [int(round(v)) for v in c]
    s = ''.join(chr(x) for x in arr if 32 <= x < 127)
    print(f'cluster {i} chars sample:', s[:200])

# Also check fractional parts specifically around repeated sequences like 67.x, 80.x, etc.
from statistics import mean

def find_repeats(target, tol=0.5):
    idxs = [i for i,n in enumerate(nums) if abs(abs(n)-target) < tol]
    return idxs

for t in [67, 80, 100, 120, 130]:
    idxs = find_repeats(t)
    if idxs:
        print(f'indexes near {t}: {idxs[:20]} (count {len(idxs)})')

# Try binary by comparing sign changes or negative outliers => 1/0
bits = []
for n in nums:
    bits.append('1' if n<0 else '0')
# find long patterns of bits lengths divisible by 8
s=''.join(bits)
print('\nNegative-based bit-string length', len(s))
# print first 200 bits
print(s[:200])

# write some outputs for manual inspection
Path('analysis_out.txt').write_text(''.join([str(f)+'\n' for f in fracs1000]))
print('\nWrote analysis_out.txt with frac*1000 values')
