import argparse
import json
import os
from scanner import scan_image_for_signatures, load_signatures
from signature_analysis import score_signature_match, cluster_fragments, fingerprint_fragment
from assembler import assemble_fragments, save_recovered
from plugins.example_proprietary import match_proprietary_header

def load_raw_fragment(image_path, offset, length=65536):
    with open(image_path, "rb") as f:
        f.seek(offset)
        return f.read(length)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--signatures", default="signatures.json")
    parser.add_argument("--block-size", type=int, default=4096)
    args = parser.parse_args()
    sigs = load_signatures(args.signatures)
    matches = scan_image_for_signatures(args.image, sigs, args.block_size)
    fragments = []
    meta = []
    for m in matches:
        offset = m.get("offset")
        if offset is None:
            continue
        frag = load_raw_fragment(args.image, offset)
        prop = match_proprietary_header(frag)
        if prop:
            m.update(prop)
        fragments.append(frag)
        meta.append(m)
    labels = cluster_fragments(fragments, n_clusters=4)
    assembled_groups = {}
    for lbl in set(labels):
        group_frags = [fragments[i] for i,l in enumerate(labels) if l==lbl]
        assembled = assemble_fragments(group_frags)
        assembled_groups[lbl] = assembled
    all_saved = []
    for lbl, assembled in assembled_groups.items():
        outdir = os.path.join(args.out, f"group_{lbl}")
        saved = save_recovered(assembled, outdir, base_name=f"group{lbl}")
        all_saved.extend(saved)
    print("Recovered files:")
    for p in all_saved:
        print(p)

if __name__ == "__main__":
    main()
