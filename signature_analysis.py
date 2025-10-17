import numpy as np
from sklearn.cluster import AgglomerativeClustering
from utils import calc_entropy, sha256hex

def fragment_features(fragment):
    ent = calc_entropy(fragment)
    length = len(fragment)
    sample = fragment[:256]
    avg_byte = float(np.mean(list(sample))) if sample else 0.0
    uniq = len(set(fragment))
    return np.array([ent, length, avg_byte, uniq], dtype=float)

def cluster_fragments(fragments, n_clusters=2):
    feats = np.array([fragment_features(f) for f in fragments])
    if len(feats) < 2:
        return [0]*len(feats)
    clusterer = AgglomerativeClustering(n_clusters=min(n_clusters, len(feats)))
    labels = clusterer.fit_predict(feats)
    return labels.tolist()

def score_signature_match(fragment, header, footer):
    hlen = len(header) if header else 0
    fscore = 0.0
    if hlen and fragment.startswith(header):
        fscore += 1.0
    if footer and fragment.endswith(footer):
        fscore += 1.0
    ent = calc_entropy(fragment)
    if 3.0 <= ent <= 7.5:
        fscore += 0.5
    return fscore

def fingerprint_fragment(fragment):
    return sha256hex(fragment[:4096])


def fuzzy_match(buffer, signature, threshold=0.8):
    matches = 0
    sig_bytes = bytes.fromhex(signature)
    for i in range(len(sig_bytes)):
        if buffer[i] == sig_bytes[i]:
            matches += 1
    return (matches / len(sig_bytes)) >= threshold
