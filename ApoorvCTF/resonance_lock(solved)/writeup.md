# Resonance Lock — Writeup

**CTF:** ApoorvCTF  
**Challenge:** Resonance Lock  
**Category:** Hardware / Misc  
**Flag:** `apoorvctf{3N7R0P1C_31D0L0N_0F_7H3_50C_4N4LY57_N0C7URN3}`

---

## Challenge Description

Phase-lock a UART baud-rate oscillator to exactly **2,345,679 baud**, exercise the 512-bit hardware multiplier, and extract the fixed flag token before the 45-second supercapacitor drains.

**Connection:** `nc chals4.apoorvctf.xyz 1337`

### Protocol (8N1 Framing)

1. **CALIBRATE** — Send byte `0xCA` (no reply expected).
2. **Calibration Burst** — Send exactly 64× `0x55` bytes with precise baud timing. Repeat until `LOCKED`.
3. **Locked Mode** (45s window) — Send `0xAA` + 64-byte A + 64-byte B (512-bit big-endian operands) → receive the flag.

### Critical Constraints

- **HSM tamper fuse** is one-time per TCP session. Sending garbage bytes, JTAG/SWD commands, flash reads, or wrong patterns permanently blows the fuse for that session: `ERR:HSM_TAMPER_FUSE_BLOWN`.
- `TCP_NODELAY` is required; bytes must be sent individually with precise inter-byte timing.
- The server times only the last 63 bytes (the first byte acts as a trigger).

---

## Solution

### Step 1: Understanding the Timing

In UART 8N1, each byte is 10 bits (1 start + 8 data + 1 stop). At 2,345,679 baud:

$$
T_{\text{byte}} = \frac{10}{2{,}345{,}679} \approx 4.263\;\mu\text{s} \;(4263\;\text{ns})
$$

The server measures the total transmission time for 63 inter-byte gaps (bytes 2–64, since byte 1 is a trigger):

$$
T_{\text{expected}} = 63 \times 4263 = 268{,}569\;\text{ns}
$$

### Step 2: Initial Mistake — Fuse Blown

My first attempt sent the literal text `"CALIBRATE\n"` to the server, which it interpreted as garbage bytes → **fuse blown instantly**. The challenge description says "Enter CALIBRATE" meaning you enter the calibration *state* by sending byte `0xCA`, not the ASCII string.

### Step 3: Correct Protocol — Send `0xCA` First

On a fresh connection, sending the single byte `\xCA` puts the HSM into calibration mode without blowing the fuse. No response is expected.

### Step 4: Calibration Burst Loop

Each calibration burst:

1. Build a 64-byte payload of `0x55` (binary `01010101` — a classic UART clock-recovery pattern).
2. Send using precise busy-wait timing with `time.perf_counter_ns()` (OS sleep is too coarse for ~4 µs intervals).
3. Parse the server's `EXEC_TIME:<ns>` response — the server-measured total time for the 63 timed bytes.
4. Adjust the inter-byte delay:

$$
T_{\text{new}} = T_{\text{current}} \times \frac{T_{\text{expected}}}{T_{\text{measured}}}
$$

The server responses during calibration looked like:

```
Burst 0: EXEC_TIME:268380   → ratio 1.000704, adjusted to 4266 ns
Burst 1: EXEC_TIME:268380   → ratio 1.000704, adjusted to 4269 ns
Burst 2: EXEC_TIME:268380   → ratio 1.000704, adjusted to 4272 ns
Burst 3: EXEC_TIME:268380   → adjusted to 4275 ns
Burst 4: EXEC_TIME:268380   → LOCKED
```

After just 5 bursts the server reported `LOCKED` — the measured timing was within the ≤1,000 PPM threshold for 5 consecutive bursts.

### Step 5: Extract the Flag

Once locked, send the multiply command:

```
0xAA + 64-byte A + 64-byte B
```

Any valid 512-bit operands work (the flag is constant). I used `A = 2`, `B = 3` (zero-padded to 64 bytes, big-endian).

The server immediately responded:

```
FLAG:apoorvctf{3N7R0P1C_31D0L0N_0F_7H3_50C_4N4LY57_N0C7URN3}
```

---

## Key Takeaways

1. **Don't send ASCII text** — the protocol is binary. Sending `"CALIBRATE\n"` instead of `\xCA` blows the tamper fuse immediately.
2. **`TCP_NODELAY` is essential** — Nagle's algorithm would batch our carefully-timed single-byte sends into one packet, destroying the timing.
3. **Busy-wait, not sleep** — `time.sleep()` has millisecond-scale granularity on most OSes; `time.perf_counter_ns()` busy-wait achieves the ~4 µs precision required.
4. **Server-side feedback loop** — The `EXEC_TIME` response allows a simple proportional adjustment to converge on the correct timing in just a few iterations.
5. **The flag is fixed** — no actual 512-bit multiplication result is checked; any valid operand pair triggers the flag. The multiplier exercise is a gate, not a computation.

---

## Solve Script

```python
import socket
import time

HOST = "chals4.apoorvctf.xyz"
PORT = 1337
BAUD = 2_345_679
BYTE_TIME_NS = round(10 / BAUD * 1_000_000_000)  # ~4263 ns

def recv_all(sock, timeout=3):
    sock.settimeout(timeout)
    data = b""
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
    except socket.timeout:
        pass
    return data

def send_timed_burst(sock, data, byte_time_ns):
    sock.send(data[0:1])  # trigger byte (not timed)
    start = time.perf_counter_ns()
    for i in range(1, len(data)):
        target = start + i * byte_time_ns
        while time.perf_counter_ns() < target:
            pass
        sock.send(data[i:i+1])
    return time.perf_counter_ns() - start

def solve():
    expected_ns = 63 * BYTE_TIME_NS  # 268569 ns

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.connect((HOST, PORT))

    recv_all(sock, 2)        # discard banner
    sock.sendall(b"\xCA")    # enter calibration
    recv_all(sock, 2)

    byte_time_ns = BYTE_TIME_NS
    for attempt in range(60):
        burst = bytes([0x55] * 64)
        send_timed_burst(sock, burst, byte_time_ns)
        resp = recv_all(sock, 5).decode(errors='replace').strip()

        if "LOCKED" in resp:
            break
        if "TAMPER" in resp:
            sock.close()
            return

        for line in resp.split('\n'):
            if line.strip().startswith("EXEC_TIME:"):
                exec_time = int(line.strip().split(":")[1])
                byte_time_ns = int(byte_time_ns * expected_ns / exec_time)

    # Send multiply operands → get flag
    A = b"\x00" * 63 + b"\x02"
    B = b"\x00" * 63 + b"\x03"
    sock.sendall(b"\xAA" + A + B)
    print(recv_all(sock, 15).decode(errors='replace').strip())
    sock.close()

solve()
```

---

## Flag

```
apoorvctf{3N7R0P1C_31D0L0N_0F_7H3_50C_4N4LY57_N0C7URN3}
```
