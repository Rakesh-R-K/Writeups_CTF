from pathlib import Path
import math

p = Path('c:/Users/Rakesh R K/Downloads/bitsctf/radio_telescope/rt7-log.txt')
lines = [l.strip() for l in p.read_text().splitlines() if l.strip()]
nums = [float(l) for l in lines]

# build clusters where consecutive difference < 1.0
clusters = []
cur = [nums[0]]
for x,y in zip(nums, nums[1:]):
    if abs(y-x) < 1.0:
        cur.append(y)
    else:
        clusters.append(cur)
        cur=[y]
clusters.append(cur)

# For clusters with length >= 5, map to a char by rounding the mean
msg = []
for c in clusters:
    if len(c) >= 5:
        val = int(round(sum(c)/len(c)))
        if 32 <= val < 127:
            msg.append(chr(val))
        else:
            msg.append('?')
    else:
        # for small segments, map to '.'
        msg.append('.')

out = ''.join(msg)
print('Clusters count:', len(clusters))
print(out)
# Also print only the printable chars sequence
print('Printable sequence:',''.join(ch for ch in msg if ch!='.'))

# Save to file
Path('extracted_message.txt').write_text(out)
