#!/usr/bin/env python3

# Manual decoding based on Whitespace specification
# In Whitespace: Space=0, Tab=1 for numbers

with open('They_call_me_Cutie.txt', 'r') as f:
    lines = f.readlines()

decoded = []

for line in lines:
    # Remove leading/trailing whitespace for analysis
    stripped = line.strip()
    if not stripped:
        continue
    
    # Each line format: S S S S S [binary with S and T] L T L
    # Example: "S S S T S S S S T S L" 
    # After "S S S": T=1, S=0 for binary encoding
    
    # Split by tabs and spaces more carefully
    tokens = []
    for char in stripped:
        if char == 'S':
            tokens.append('S')
        elif char == 'T':
            tokens.append('T')
        elif char == 'L':
            tokens.append('L')
    
    # Find pattern: After initial "S S" (push), read binary until "L"
    if len(tokens) >= 4 and tokens[0] == 'S' and tokens[1] == 'S':
        # Start reading from position 2 (after push instruction)
        binary = ''
        i = 2
        
        # Skip initial S (sign bit: S=positive)
        if i < len(tokens) and tokens[i] == 'S':
            i += 1
        
        # Read binary digits until we hit 'L'
        while i < len(tokens) and tokens[i] != 'L':
            if tokens[i] == 'S':
                binary += '0'
            elif tokens[i] == 'T':
                binary += '1'
            i += 1
        
        if binary:
            try:
                ascii_val = int(binary, 2)
                if 32 <= ascii_val <= 126:
                    decoded.append(chr(ascii_val))
                    print(f"Binary: {binary} -> {ascii_val} -> '{chr(ascii_val)}'")
            except:
                pass

print("\nFinal decoded message:")
print(''.join(decoded))
