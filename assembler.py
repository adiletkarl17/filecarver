import os
from collections import defaultdict
from utils import calc_entropy, sha256hex

def find_overlaps(a, b, min_overlap=16):
    max_ov = 0
    la = len(a)
    lb = len(b)
    limit = min(1024, la, lb)
    for l in range(limit, min_overlap-1, -1):
        if a[-l:] == b[:l]:
            return l
    return 0

def assemble_fragments(fragments):
    assembled = []
    used = set()
    frag_map = {i:fr for i,fr in enumerate(fragments)}
    while True:
        remaining = [i for i in frag_map.keys() if i not in used]
        if not remaining:
            break
        seed = remaining[0]
        used.add(seed)
        buffer = bytearray(frag_map[seed])
        changed = True
        while changed:
            changed = False
            for i in remaining:
                if i in used:
                    continue
                ov = find_overlaps(buffer, frag_map[i], min_overlap=8)
                if ov > 0:
                    buffer.extend(frag_map[i][ov:])
                    used.add(i)
                    changed = True
            for i in remaining:
                if i in used:
                    continue
                ov = find_overlaps(frag_map[i], buffer, min_overlap=8)
                if ov > 0:
                    newbuf = bytearray(frag_map[i])
                    newbuf.extend(buffer[ov:])
                    buffer = newbuf
                    used.add(i)
                    changed = True
        assembled.append(bytes(buffer))
    return assembled

def save_recovered(assembled, out_dir, base_name="recovered"):
    os.makedirs(out_dir, exist_ok=True)
    saved = []
    for idx, data in enumerate(assembled):
        name = f"{base_name}_{idx}.bin"
        path = os.path.join(out_dir, name)
        with open(path, "wb") as f:
            f.write(data)
        saved.append(path)
    return saved
