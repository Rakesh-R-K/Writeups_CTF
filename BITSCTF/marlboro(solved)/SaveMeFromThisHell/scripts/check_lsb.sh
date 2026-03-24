#!/bin/bash
for f in "/mnt/c/Users/Rakesh R K/Downloads/bitsctf/marlboro/SaveMeFromThisHell/output/zip/00007332/lsb"/*.bin; do
  printf "==%s\n" "$f"
  grep -a -n 'BITSCTF{' "$f" || true
  file "$f"
  od -An -t x1 -N 16 "$f" | sed -n '1,1p'
done
