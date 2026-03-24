import socket
import time
import sys

HOST = "chals4.apoorvctf.xyz"
PORT = 1337
BAUD = 2_345_679
BYTE_TIME_S = 10.0 / BAUD  # ~4.263 µs per byte (10 bits in 8N1)
BYTE_TIME_NS = int(BYTE_TIME_S * 1_000_000_000)

def recv_until(sock, timeout=5):
    """Receive all available data."""
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

def recv_line(sock, timeout=10):
    """Receive until newline."""
    sock.settimeout(timeout)
    buf = b""
    try:
        while b"\n" not in buf:
            chunk = sock.recv(1)
            if not chunk:
                break
            buf += chunk
    except socket.timeout:
        pass
    return buf

def send_timed_burst(sock, data, byte_time_ns):
    """Send bytes with precise inter-byte busy-wait timing."""
    # First byte is trigger only (not timed)
    sock.send(data[0:1])
    start = time.perf_counter_ns()
    for i in range(1, len(data)):
        target = start + i * byte_time_ns
        while time.perf_counter_ns() < target:
            pass
        sock.send(data[i:i+1])

def solve():
    print(f"Target baud: {BAUD}")
    print(f"Byte time: {BYTE_TIME_S*1e6:.3f} µs ({BYTE_TIME_NS} ns)")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.connect((HOST, PORT))
    print(f"Connected to {HOST}:{PORT}")
    
    # Read initial banner
    banner = recv_until(sock, 3)
    print(f"Banner: {banner!r}")
    
    # Step 1: Enter CALIBRATE mode
    sock.sendall(b"CALIBRATE\n")
    resp = recv_until(sock, 3)
    print(f"After CALIBRATE: {resp!r}")
    
    # Step 2: Send 0xCA
    sock.sendall(b"\xCA")
    resp = recv_until(sock, 3)
    print(f"After 0xCA: {resp!r}")
    
    # Step 3: Calibration bursts
    byte_time_ns = BYTE_TIME_NS
    consecutive_good = 0
    locked = False
    
    for attempt in range(50):
        burst = bytes([0x55] * 64)
        send_timed_burst(sock, burst, byte_time_ns)
        
        resp = recv_until(sock, 5)
        resp_str = resp.decode(errors='replace').strip()
        print(f"Burst {attempt}: {resp_str}")
        
        if "LOCKED" in resp_str:
            print("=== LOCKED ===")
            locked = True
            break
        
        if "TAMPER" in resp_str or "FUSE" in resp_str:
            print("!!! FUSE BLOWN - need fresh connection !!!")
            sock.close()
            return
        
        if "ERR:" in resp_str:
            # Parse PPM error like ERR:+00123 or ERR:-00045
            try:
                for line in resp_str.split('\n'):
                    if 'ERR:' in line and ('+' in line or '-' in line):
                        err_part = line.split('ERR:')[1].strip()
                        ppm = int(err_part)
                        print(f"  PPM error: {ppm}")
                        
                        if abs(ppm) <= 1000:
                            consecutive_good += 1
                            print(f"  Good burst {consecutive_good}/5")
                        else:
                            consecutive_good = 0
                            # Adjust: positive PPM = too slow, negative = too fast
                            # New interval = old / (1 + ppm/1e6)
                            factor = 1.0 + ppm / 1_000_000.0
                            byte_time_ns = int(byte_time_ns / factor)
                            print(f"  Adjusted byte_time_ns: {byte_time_ns}")
                        break
            except Exception as e:
                print(f"  Parse error: {e}")
    
    if not locked:
        print("Failed to achieve lock")
        sock.close()
        return
    
    # Step 4: Locked mode - send multiply operands
    # 0xAA + 64-byte A + 64-byte B (512-bit big-endian)
    A = b"\x00" * 63 + b"\x01"  # A = 1
    B = b"\x00" * 63 + b"\x01"  # B = 1
    payload = b"\xAA" + A + B
    
    print(f"Sending multiply payload ({len(payload)} bytes)...")
    sock.sendall(payload)
    
    # Wait for flag
    resp = recv_until(sock, 15)
    resp_str = resp.decode(errors='replace').strip()
    print(f"Response: {resp_str}")
    
    if "FLAG" in resp_str or "apoorv" in resp_str:
        print(f"\n*** FLAG: {resp_str} ***")
    
    sock.close()

if __name__ == "__main__":
    solve()
