#!/bin/bash
for f in "/mnt/c/Users/Rakesh R K/Downloads/bitsctf/marlboro/SaveMeFromThisHell/output/zip/00007332/carved"/*.zip; do
  printf "==%s\n" "$f"
  file "$f"
  unzip -l "$f" 2>/dev/null || echo 'not a valid zip or no central directory'
done
