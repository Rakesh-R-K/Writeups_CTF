#!/usr/bin/env python3
import base64
import subprocess
import sys
from collections import defaultdict


def run_tshark(pcap_path: str):
    cmd = [
        "tshark",
        "-r",
        pcap_path,
        "-Y",
        "dns.flags.response==0",
        "-T",
        "fields",
        "-E",
        "separator=\t",
        "-e",
        "frame.number",
        "-e",
        "ip.src",
        "-e",
        "dns.qry.name",
    ]
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    rows = []
    for line in proc.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        frame_no, src, qname = parts[0].strip(), parts[1].strip(), parts[2].strip()
        if not frame_no or not src or not qname:
            continue
        rows.append((int(frame_no), src, qname))
    return rows


def extract_payload_chunks(queries):
    by_src = defaultdict(list)
    for frame_no, src, qname in queries:
        by_src[src].append((frame_no, qname))

    # In this challenge, the exfil host is the unique one with exactly six DNS queries.
    candidates = [src for src, items in by_src.items() if len(items) == 6]
    if len(candidates) != 1:
        raise RuntimeError(f"Expected one six-query source, found: {candidates}")

    attacker_ip = candidates[0]
    records = sorted(by_src[attacker_ip], key=lambda x: x[0])

    indexed_chunks = []
    for _, qname in records:
        labels = qname.split(".")
        if len(labels) < 5:
            raise RuntimeError(f"Unexpected DNS name format: {qname}")
        idx = int(labels[1])
        chunk_b64 = labels[2]
        indexed_chunks.append((idx, chunk_b64))

    indexed_chunks.sort(key=lambda x: x[0])
    raw = b"".join(base64.b64decode(chunk) for _, chunk in indexed_chunks)
    return attacker_ip, raw


def decode_flag(raw: bytes):
    prefix = b"CrackOn{"
    for key in range(256):
        candidate = bytes(b ^ key for b in raw)
        if candidate.startswith(prefix) and candidate.endswith(b"}"):
            return key, candidate.decode("ascii")
    raise RuntimeError("Could not decode flag with single-byte XOR")


def main():
    pcap_path = sys.argv[1] if len(sys.argv) > 1 else "knoten_in_the_wire.pcap"
    queries = run_tshark(pcap_path)
    attacker_ip, raw = extract_payload_chunks(queries)
    key, flag = decode_flag(raw)

    print(f"Attacker IP: {attacker_ip}")
    print(f"XOR key: 0x{key:02x}")
    print(f"Flag: {flag}")


if __name__ == "__main__":
    main()
