#!/usr/bin/env python3
"""Solve script for rusty_frame challenge.

Usage:
  python3 solve.py [path/to/binary] [file_arg]

Defaults: binary is './rusty_frame_S6NV0Zx', file_arg is '/etc/passwd'
"""
import sys
import os
import subprocess


def main():
    bin_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), 'rusty_frame_S6NV0Zx')
    target = sys.argv[2] if len(sys.argv) > 2 else '/etc/passwd'

    if not os.path.isabs(bin_path) and not os.path.exists(bin_path):
        bin_path = os.path.join(os.getcwd(), bin_path)

    try:
        cmd = [bin_path, target]
        print('Running:', cmd, file=sys.stderr)
        proc = subprocess.run(cmd, capture_output=True, timeout=10)
        out = proc.stdout.decode(errors='replace')
        if out:
            print(out, end='')
        else:
            print('No output from binary. Tried:', bin_path, target, file=sys.stderr)
            if proc.stderr:
                print('STDERR:', proc.stderr.decode(errors='replace'), file=sys.stderr)
            sys.exit(1)
    except FileNotFoundError:
        print('Binary not found:', bin_path, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print('Error running binary:', e, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
