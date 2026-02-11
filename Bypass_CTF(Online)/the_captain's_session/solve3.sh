#!/bin/bash
# Try different URL formats

URL="http://20.196.136.66:1692/webhook"

# Try variations
variations=(
    "https://isdf.dev/"
    "https://isdf.dev"
    "http://isdf.dev/"
    "http://isdf.dev"
    "isdf.dev"
    "isdf.dev/"
    "www.isdf.dev"
)

for answer in "${variations[@]}"; do
    echo "Trying: $answer"
    RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
      -d "{\"step\": 1, \"answer\": \"$answer\"}" "$URL")
    
    if echo "$RESPONSE" | grep -q '"flag_part"'; then
        echo "SUCCESS with: $answer"
        echo "Response: $RESPONSE"
        PART1=$(echo "$RESPONSE" | grep -o '"flag_part":"[^"]*' | cut -d'"' -f4)
        echo "Flag part 1: $PART1"
        
        # Now try step 2
        echo ""
        echo "Trying step 2 with: stepped_on"
        RESPONSE2=$(curl -s -X POST -H "Content-Type: application/json" \
          -d '{"step": 2, "answer": "stepped_on"}' "$URL")
        echo "Response: $RESPONSE2"
        
        PART2=$(echo "$RESPONSE2" | grep -o '"flag_part":"[^"]*' | cut -d'"' -f4)
        if [ -n "$PART2" ]; then
            echo "Flag part 2: $PART2"
            echo ""
            echo "Complete flag: ${PART1}${PART2}"
        fi
        exit 0
    else
        echo "Failed: $RESPONSE"
    fi
    echo ""
done
