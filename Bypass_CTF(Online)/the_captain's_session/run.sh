#!/bin/bash
# Usage: bash interact.sh

URL="http://20.196.136.66:1692/webhook"

echo "What is the url of the bookmarked website?"
read -r Q1
RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"step": 1, "answer": "'"$Q1"'"}' "$URL")
if echo "$RESPONSE" | grep -q 'error'; then
  exit 1
fi
PART1=$(echo "$RESPONSE" | grep -o '"flag_part":"[^"]*' | cut -d'"' -f4)
if [ -n "$PART1" ]; then
  echo "Flag part 1: $PART1"
else
  exit 1
fi

echo "What is the password?"
read -r Q2
RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"step": 2, "answer": "'"$Q2"'"}' "$URL")
if echo "$RESPONSE" | grep -q 'error'; then
  exit 1
fi
PART2=$(echo "$RESPONSE" | grep -o '"flag_part":"[^"]*' | cut -d'"' -f4)
PIRATE_MSG=$(echo "$RESPONSE" | grep -o '"pirate_msg":"[^"]*' | cut -d'"' -f4)
if [ -n "$PART2" ]; then
  echo "Flag part 2: $PART2"
  if [ -n "$PIRATE_MSG" ]; then
    echo "$PIRATE_MSG"
  fi
else
  exit 1
fi