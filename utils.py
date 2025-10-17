import math
import hashlib

def calc_entropy(data):
    if not data:
        return 0.0
    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    ent = 0.0
    ln2 = math.log(2)
    n = len(data)
    for v in freq.values():
        p = v / n
        ent -= p * (math.log(p) / ln2)
    return ent

def rolling_hash(bytes_seq, base=257, mod=(1<<61)-1):
    h = 0
    for b in bytes_seq:
        h = (h * base + b) % mod
    return h

def sha256hex(data):
    return hashlib.sha256(data).hexdigest()

def read_chunks(fileobj, chunk_size):
    while True:
        chunk = fileobj.read(chunk_size)
        if not chunk:
            break
        yield chunk
