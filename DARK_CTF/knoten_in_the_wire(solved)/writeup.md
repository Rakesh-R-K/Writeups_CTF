# Knoten in the Wire - Forensics Writeup

## Challenge Summary
We are given a packet capture file named knoten_in_the_wire.pcap and told that:
- Five residents generate high-volume normal traffic.
- A sixth machine (not one of the five) exfiltrates data through DNS.
- The covert channel uses six DNS queries.
- The final flag format is CrackOn{...}.

## Environment and Tools Used
- Host OS: Windows
- Analysis runtime: WSL
- Main tools: tshark, python3

## Step 1: Identify the Suspicious Host
Count DNS query sources:

```bash
wsl tshark -r knoten_in_the_wire.pcap -Y "dns.flags.response==0" -T fields -e ip.src | sort | uniq -c | sort -nr
```

Observed counts included:
- 192.168.33.30 -> 481
- 192.168.33.40 -> 466
- 192.168.33.20 -> 466
- 192.168.33.60 -> 450
- 192.168.33.50 -> 437
- 10.33.19.86 -> 6

The unique six-query source is 10.33.19.86, matching the challenge hint.

## Step 2: Extract the Six Covert DNS Queries

```bash
wsl tshark -r knoten_in_the_wire.pcap -Y "dns.flags.response==0 and ip.src==10.33.19.86" -T fields -e frame.number -e dns.qry.name
```

Recovered queries:
1. jonas.0.DTwvLSUB.winden-cave.local
2. noah.1.IDUlIH46.winden-cave.local
3. claudia.2.KyARLXo4.winden-cave.local
4. adam.3.fRE6fyN9.winden-cave.local
5. eva.4.ESJ+fj4R.winden-cave.local
6. tannhaus.5.Ojx6LX0qMw==.winden-cave.local

Pattern found:
- label 2 is an index (0..5)
- label 3 is a base64 chunk

## Step 3: Decode the Exfil Payload
Decoding process:
1. Sort chunks by index.
2. Base64-decode each chunk.
3. Concatenate bytes.
4. Apply single-byte XOR brute force.
5. Select candidate beginning with CrackOn{ and ending with }.

The valid decode key is:
- XOR key: 0x4e

Decoded flag string:
- CrackOn{kn0ten_c4v3_t1m3_l00p_tr4c3d}

## Local Solver Script
A reproducible solver script was created:
- solve_dns_exfil.py

Run command:

```bash
wsl python3 solve_dns_exfil.py
```

Script output:
- Attacker IP: 10.33.19.86
- XOR key: 0x4e
- Flag: CrackOn{kn0ten_c4v3_t1m3_l00p_tr4c3d}

## Final Flag
CrackOn{kn0ten_c4v3_t1m3_l00p_tr4c3d}
