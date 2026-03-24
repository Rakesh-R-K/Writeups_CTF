# A golden experience requiem

## Flag

`apoorvctf{1_h0pe_5BR_i5_w33kly_rele4as3}`

## Summary

The challenge binary is a stripped Rust ELF that contains a fake flag, several anti-analysis checks, worker threads, and a deliberate crash right after printing `loaded flag` and `printing flag.....`.

The real flag is not stored directly. It is generated at runtime into a mapped memory page, one byte at a time.

## Initial Recon

The file is a 64-bit Linux ELF:

```text
ELF 64-bit LSB pie executable, x86-64, stripped
```

Useful strings include:

```text
apoorvctf{wh4t_1f_k1ng_cr1ms0n_requ13m3d??}
loaded flag
printing flag.....
```

The embedded `apoorvctf{wh4t_1f_k1ng_cr1ms0n_requ13m3d??}` is a fake flag.

Running the program only gives:

```text
loaded flag
printing flag.....
```

and then the process crashes intentionally.

## Anti-Analysis

The binary decodes and checks several common analysis indicators:

- `qemu`
- `valgrind`
- `PIN_ROOT`
- `libasan`
- `ltrace`
- `librrpreload`

These checks control a global state that slightly alters the output if analysis is detected.

The binary also restores default `SIGSEGV` handling before the final crash, which is meant to prevent an easy dump through a custom handler.

## Fake Flag Path

There is one direct code reference to the fake flag string in `.rodata`.

Only the first 16 bytes are used:

```text
apoorvctf{wh4t_1
```

Those 16 bytes are transformed through a 256-byte lookup table that turns out to be the AES S-box. A small permutation is then applied to positions `1, 5, 9, 13`.

A second 16-byte block from `.rodata` is transformed through the same S-box.

These transformed blocks are intermediate values, not the final flag.

## Real Flag Logic

The important worker routine writes 40 bytes into a mapped output page. For each index `n` from `0` to `39`, it computes one byte using:

1. A per-index arithmetic term:

```text
left = ((7*n + 63) mod 256) XOR rol8(n, 3)
```

2. A byte extracted from the SHA-256 IV constants:

```text
6a09e667
bb67ae85
3c6ef372
a54ff53a
510e527f
9b05688c
1f83d9ab
5be0cd19
```

3. A byte from one of two 20-byte tables in `.rodata`.

Even-index table:

```text
39407691b717c97879013adf3a2adea11c2b04e0
```

Odd-index table:

```text
bb19b025e37eaa786c4116e7aeea00c9c623940d
```

The final byte formula is:

```text
out[n] = left XOR sha_byte(n) XOR table_byte(n)
```

where:

- `sha_byte(n)` is selected from the SHA-256 IV words using the same indexing pattern as the worker routine
- `table_byte(n)` comes from the even or odd table depending on whether `n` is even or odd

## Reconstructed Output

Rebuilding all 40 bytes offline gives:

```text
61706f6f72766374667b315f683070655f3542525f69355f7733336b6c795f72656c65346173337d
```

ASCII decoding of that hex is:

```text
apoorvctf{1_h0pe_5BR_i5_w33kly_rele4as3}
```

## Why The Program Crashes

After the worker threads finish generating the flag page, the main thread prints:

```text
loaded flag
printing flag.....
```

and then deliberately faults. The crash is only anti-reversing noise. The flag generation already happened before that point.

## Final Answer

`apoorvctf{1_h0pe_5BR_i5_w33kly_rele4as3}`