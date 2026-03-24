import socket
import time
import sys

HOST = "chals4.apoorvctf.xyz"
PORT = 1337
BAUD = 2_345_679
# 10 bits per byte in 8N1 (1 start + 8 data + 1 stop)
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
    """Send bytes with precise inter-byte busy-wait timing.
       First byte is trigger (not timed). Server times bytes 2-64."""
    sock.send(data[0:1])
    start = time.perf_counter_ns()
    for i in range(1, len(data)):
        target = start + i * byte_time_ns
        while time.perf_counter_ns() < target:
            pass
        sock.send(data[i:i+1])
    elapsed = time.perf_counter_ns() - start
    return elapsed

def solve():
    print(f"Target baud: {BAUD}")
    print(f"Nominal byte time: {BYTE_TIME_NS} ns ({BYTE_TIME_NS/1000:.3f} µs)")
    # Expected time for 63 inter-byte gaps: 63 * BYTE_TIME_NS
    expected_ns = 63 * BYTE_TIME_NS
    print(f"Expected total for 63 bytes: {expected_ns} ns ({expected_ns/1000:.1f} µs)")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.connect((HOST, PORT))
    print(f"Connected to {HOST}:{PORT}")
    
    # Read initial data
    data = recv_all(sock, 2)
    if data:
        print(f"Initial: {data!r}")
    
    # Step 1: Send 0xCA to enter calibration mode
    print("\n--- Sending 0xCA ---")
    sock.sendall(b"\xCA")
    data = recv_all(sock, 2)
    print(f"After 0xCA: {data!r}")
    
    # Step 2: Calibration bursts
    byte_time_ns = BYTE_TIME_NS
    consecutive_good = 0
    locked = False
    
    for attempt in range(60):
        burst = bytes([0x55] * 64)
        elapsed = send_timed_burst(sock, burst, byte_time_ns)
        
        data = recv_all(sock, 5)
        resp_str = data.decode(errors='replace').strip()
        print(f"\nBurst {attempt} (local elapsed: {elapsed} ns, byte_time: {byte_time_ns} ns):")
        
        for line in resp_str.split('\n'):
            line = line.strip()
            if line:
                print(f"  {line}")
        
        if "LOCKED" in resp_str:
            print("\n=== LOCKED ===")
            locked = True
            break
        
        if "TAMPER" in resp_str or "FUSE" in resp_str:
            print("\n!!! FUSE BLOWN !!!")
            sock.close()
            return None
        
        # Parse EXEC_TIME and ERR
        exec_time = None
        ppm_err = None
        for line in resp_str.split('\n'):
            line = line.strip()
            if line.startswith("EXEC_TIME:"):
                try:
                    exec_time = int(line.split(":")[1])
                except:
                    pass
            if line.startswith("ERR:"):
                try:
                    err_part = line.split("ERR:")[1].strip()
                    if err_part[0] in '+-':
                        ppm_err = int(err_part)
                except:
                    pass
        
        if exec_time is not None:
            print(f"  Server measured: {exec_time} ns, expected: {expected_ns} ns")
            # Adjust byte_time based on server's measurement
            # If exec_time > expected, we're too slow -> decrease byte_time
            # If exec_time < expected, we're too fast -> increase byte_time
            # ratio = exec_time / expected_ns
            # We want actual total time to equal expected, so:
            # new_byte_time = byte_time * expected_ns / exec_time
            ratio = expected_ns / exec_time
            byte_time_ns = int(byte_time_ns * ratio)
            print(f"  Ratio: {ratio:.6f}, new byte_time: {byte_time_ns} ns")
        
        if ppm_err is not None:
            print(f"  PPM error: {ppm_err}")
            if abs(ppm_err) <= 1000:
                consecutive_good += 1
                print(f"  Good burst {consecutive_good}/5")
            else:
                consecutive_good = 0
                # Also adjust based on PPM
                factor = 1.0 + ppm_err / 1_000_000.0
                byte_time_ns = int(byte_time_ns / factor)
                print(f"  PPM-adjusted byte_time: {byte_time_ns} ns")
    
    if not locked:
        print("Failed to lock!")
        sock.close()
        return None
    
    # Step 3: Locked mode - send 0xAA + 64-byte A + 64-byte B
    A = b"\x00" * 63 + b"\x02"  # A = 2
    B = b"\x00" * 63 + b"\x03"  # B = 3
    payload = b"\xAA" + A + B
    
    print(f"\nSending multiply payload ({len(payload)} bytes)...")
    sock.sendall(payload)
    
    resp = recv_all(sock, 15)
    resp_str = resp.decode(errors='replace').strip()
    print(f"Response: {resp_str}")
    
    if "apoorv" in resp_str or "FLAG" in resp_str:
        print(f"\n*** FLAG FOUND ***")
        # Extract the flag
        for line in resp_str.split('\n'):
            if 'apoorv' in line or 'FLAG' in line:
                print(line.strip())
    
    sock.close()
    return resp_str

if __name__ == "__main__":
    result = solve()
