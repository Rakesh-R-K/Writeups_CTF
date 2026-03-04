# rusty_frame — writeup

## Summary

This challenge is a small ELF64 Linux binary (stripped, PIE) built from Rust. The program prints a flag when invoked with a filename/argument.

## Files

- `rusty_frame_S6NV0Zx` — challenge binary (ELF64, dynamically linked, stripped)

## Analysis

1. Identified file type and architecture:

   - `file rusty_frame_S6NV0Zx` → ELF 64-bit LSB, x86-64, dynamically linked, stripped, PIE.

2. Looked for readable strings and clues:

   - `strings` and `.rodata` inspection revealed `RUSTY_WIN` and many Rust panic/backtrace strings.

3. Ran the binary and probed its behaviour with inputs and arguments.

   - Running the binary with no args produced no visible output.
   - Passing arbitrary filename arguments (for example `/etc/passwd`) produced a short 24-byte output that contained the flag.

## Solution / Exploit

The binary prints the flag when invoked with a filename argument. Example command:

```
./rusty_frame_S6NV0Zx /etc/passwd
```

This prints:

```
bpctf{stand_proud_mate}
```

No further memory corruption or complex exploit was required; passing a filename argument triggers the code path that prints the flag.

## Flag

bpctf{stand_proud_mate}

## Notes

- The binary is stripped and contains many Rust-related strings, but the simplest route was runtime probing.
- If you want, you can create a small script to call the binary with a file path and capture the flag automatically.
