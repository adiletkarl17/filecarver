def match_proprietary_header(data):
    pattern = b"DRONEIMG"
    if data.startswith(pattern):
        return {"format":"drone_proprietary","header_len":len(pattern)}
    return None
