import os
import json
from tqdm import tqdm
from utils import sha256hex

def load_signatures(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def bytes_from_hex(h):
    return bytes.fromhex(h) if h else None

def scan_image_for_signatures(image_path, sigs, block_size=4096):
    matches = []
    headers = [(s["name"], bytes_from_hex(s.get("header")), bytes_from_hex(s.get("footer")), s.get("min_size",0), s.get("max_size",2**30)) for s in sigs["formats"]]
    file_size = os.path.getsize(image_path)
    with open(image_path, "rb") as f:
        pos = 0
        pbar = tqdm(total=file_size, unit="B", unit_scale=True)
        while True:
            buf = f.read(block_size)
            if not buf:
                break
            for name, header, footer, min_s, max_s in headers:
                if header and buf.startswith(header):
                    matches.append({"offset": pos, "format": name, "header_len": len(header), "footer": footer, "min_size": min_s, "max_size": max_s})
                if header and header in buf and buf.index(header) != 0:
                    idx = buf.index(header)
                    matches.append({"offset": pos+idx, "format": name, "header_len": len(header), "footer": footer, "min_size": min_s, "max_size": max_s})
                if footer and footer in buf:
                    idx = buf.index(footer)
                    matches.append({"footer_offset": pos+idx+len(footer), "format": name})
            pos += len(buf)
            pbar.update(len(buf))
        pbar.close()
    for m in matches:
        m["id"] = sha256hex(f"{m.get('offset',m.get('footer_offset'))}_{m.get('format')}".encode())
    return matches
