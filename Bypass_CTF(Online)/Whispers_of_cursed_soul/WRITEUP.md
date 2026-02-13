# Bypass CTF Challenge Writeup : Whispers of Cursed Soul
## Challenge Description
> An old pirate scroll has resurfaced from the depths of the sea.
> It looks ordinary… maybe even some code.
> 
> But sailors who dismissed it were never seen again.
> 
> Legends say the message was hidden not in what is written,
> 
> The sea doesn't shout its secrets.
> Only those who read between the lines survive. ☠️⚓
> 
> Don't trust me I am Lier...

## Challenge Overview

This is a steganography/esoteric programming language challenge involving:
- Hidden data in whitespace characters
- Whitespace programming language
- File analysis and pattern recognition
- Binary encoding within whitespace tokens

The challenge provides a text file (`They_call_me_Cutie.txt`) that appears to contain some kind of code, but the real message is hidden in the whitespace characters themselves.

## Analysis

### Understanding the Clues

The challenge description is packed with hints:

- **"hidden not in what is written"** → The visible characters (S, T, L) are just placeholders
- **"read between the lines"** → Focus on whitespace/invisible characters
- **"The sea doesn't shout its secrets"** → The message is subtle, hidden
- **"Don't trust me I am Lier"** → Suspicious wording... "Lier" instead of "Liar"
  - Could be hinting at **L**ine, but more importantly...
  - The capitalization is odd: **L**ier
  - This might hint at the three token types: **S** (Space), **T** (Tab), **L** (Line feed)

### Initial File Examination

Looking at `They_call_me_Cutie.txt`, we see:

```
S S S T	S S S S T	S L
T	L
S S S S S T	S T	T	S S T	L
T	L
S S S S S T	S T	S S S S L
T	L
...
```

At first glance, it looks like some kind of code with S, T, and L characters separated by whitespace. But this is actually a red herring!

### The Key Insight: Whitespace Programming Language

The critical realization is that this is **Whitespace** - an esoteric programming language that uses only three characters:
- **Space** (S in the visible representation)
- **Tab** (T in the visible representation)  
- **Line Feed** (L in the visible representation)

In actual Whitespace code, these would be invisible! The S, T, L characters are just a **visible representation** to make the whitespace code readable.

**Whitespace Language Basics:**

1. **Stack Operations**:
   - `[Space][Space]` - Push number to stack
   
2. **Number Encoding**:
   - After push instruction, numbers are encoded in binary
   - `[Space]` = positive sign
   - `[Tab]` = negative sign
   - Then binary digits: `[Space]` = 0, `[Tab]` = 1
   - `[Line Feed]` = end of number

3. **I/O Operations**:
   - `[Tab][Line Feed][Space][Space]` - Output character from stack

### Decoding Strategy

Each line in the file represents one character being pushed and output:

```
S S S T S S S S T S L     ← Push number (binary: 1000010)
T L                        ← Output character
```

Breaking down the first line:
- `S S` = Push instruction
- `S` = Positive sign
- `T S S S S T S` = Binary with T=1, S=0 → `1000010`
- `L` = End of number
- Binary `1000010` = Decimal 66 = ASCII 'B'

## Solution

### Manual Analysis

We can manually decode each line by:
1. Extracting the binary pattern between the push instruction and line feed
2. Converting `S` to `0` and `T` to `1`
3. Converting binary to decimal to get ASCII value
4. Converting ASCII to character

**Example for first few lines:**

| Line | Binary Pattern | Binary | Decimal | ASCII |
|------|---------------|--------|---------|-------|
| 1 | T S S S S T S | 1000010 | 66 | B |
| 2 | S T S T T S S T | 01011001 | 89 | Y |
| 3 | S T S T S S S S | 01010000 | 80 | P |
| 4 | S T S S S S S T | 01000001 | 65 | A |
| 5 | S T S T S S T T | 01010011 | 83 | S |

### Automated Solution

```python
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
```

### Execution Output

```
Binary: 1000010 -> 66 -> 'B'
Binary: 001011001 -> 89 -> 'Y'
Binary: 001010000 -> 80 -> 'P'
Binary: 001000001 -> 65 -> 'A'
Binary: 001010011 -> 83 -> 'S'
Binary: 001010011 -> 83 -> 'S'
Binary: 001011111 -> 95 -> '_'
Binary: 001000011 -> 67 -> 'C'
Binary: 001010100 -> 84 -> 'T'
Binary: 001000110 -> 70 -> 'F'
Binary: 001111011 -> 123 -> '{'
Binary: 001010111 -> 87 -> 'W'
Binary: 001101000 -> 104 -> 'h'
Binary: 000110001 -> 49 -> '1'
Binary: 001110100 -> 116 -> 't'
Binary: 001110011 -> 115 -> 's'
Binary: 001110000 -> 112 -> 'p'
Binary: 000110100 -> 52 -> '4'
Binary: 001100011 -> 99 -> 'c'
Binary: 000110011 -> 51 -> '3'
Binary: 001011111 -> 95 -> '_'
Binary: 001100011 -> 99 -> 'c'
Binary: 001110101 -> 117 -> 'u'
Binary: 001110100 -> 116 -> 't'
Binary: 000110001 -> 49 -> '1'
Binary: 000110011 -> 51 -> '3'
Binary: 001011111 -> 95 -> '_'
Binary: 000110001 -> 49 -> '1'
Binary: 001110100 -> 116 -> 't'
Binary: 001011111 -> 95 -> '_'
Binary: 001110111 -> 119 -> 'w'
Binary: 000110100 -> 52 -> '4'
Binary: 001110011 -> 115 -> 's'
Binary: 001111101 -> 125 -> '}'

Final decoded message:
BYPASS_CTF{Wh1tsp4c3_cut13_1t_w4s}
```

## Flag
```
BYPASS_CTF{Wh1tsp4c3_cut13_1t_w4s}
```

The flag is a clever play on words:
- **"Whitespace"** → The esoteric programming language used
- **"cutie"** → References the filename "They_call_me_Cutie.txt"
- **"it was"** → Leetspeak version confirming "it was" Whitespace!

The leetspeak (`Wh1tsp4c3`, `cut13`, `1t`, `w4s`) adds that CTF flair while clearly referencing both the programming language and the filename.

## Understanding Whitespace Language

### What is Whitespace?

Whitespace is an esoteric programming language created in 2003 that uses only three characters:
- **Space (ASCII 32)**
- **Tab (ASCII 9)**
- **Line Feed (ASCII 10)**

All other characters are ignored as comments! This means:
- The actual code is invisible in most editors
- The visible text in the file is just for human readability

### Instruction Set

**Stack Manipulation:**
- `[Space][Space]` - Push number
- `[Space][Line Feed][Space]` - Duplicate top
- `[Space][Line Feed][Tab]` - Swap top two

**Arithmetic:**
- `[Tab][Space][Space][Space]` - Addition
- `[Tab][Space][Space][Tab]` - Subtraction
- `[Tab][Space][Space][Line Feed]` - Multiplication

**I/O:**
- `[Tab][Line Feed][Space][Space]` - Output character
- `[Tab][Line Feed][Space][Tab]` - Output number

### Number Representation

Numbers are encoded in binary:
1. Sign bit: `[Space]` = positive, `[Tab]` = negative
2. Binary digits: `[Space]` = 0, `[Tab]` = 1
3. Terminated by `[Line Feed]`

**Example:**
```
[Space][Tab][Space][Space][Tab][Space][Line Feed]
```
- Sign: `[Space]` = positive
- Binary: `[Tab][Space][Space][Tab][Space]` = `10010`
- Decimal: 18

## Technical Breakdown

### File Structure Analysis

Each block in the file follows this pattern:

```
S S S [SIGN] [BINARY_DIGITS] L    ← Push number to stack
T L                                 ← Output as character
```

**Detailed breakdown of line 1:**
```
S S S T S S S S T S L
│ │ │ │ └─────────┘ │
│ │ │ │      │      └── Line feed (end of number)
│ │ │ │      └── Binary: TSSSSSTS = 1000010 = 66 = 'B'
│ │ │ └── Sign: S = positive
│ │ └── Space (part of push instruction)
│ └── Space (push instruction)
└── Space
```

### Parsing Algorithm

```python
def parse_whitespace_line(line):
    tokens = extract_tokens(line)  # Get S, T, L characters
    
    if tokens[0:2] == ['S', 'S']:  # Push instruction
        i = 2
        
        # Read sign (S=positive, T=negative)
        sign = 1 if tokens[i] == 'S' else -1
        i += 1
        
        # Read binary until Line Feed
        binary = ''
        while tokens[i] != 'L':
            binary += '0' if tokens[i] == 'S' else '1'
            i += 1
        
        # Convert to integer
        value = int(binary, 2) * sign
        return value
```

### Alternative Tools

You could also use online Whitespace interpreters:

1. **Copy the file content**
2. **Replace visible S/T/L with actual whitespace**:
   - S → Space
   - T → Tab
   - L → Line Feed
3. **Run in Whitespace interpreter**: https://vii5ard.github.io/whitespace/

Or use Python Whitespace libraries:
```bash
pip install whitespace
python -m whitespace They_call_me_Cutie.txt
```

## Why This Challenge is Clever

### The Multiple Layers of Deception

1. **Visible Misdirection**: The S, T, L characters look like code but are just markers
2. **Esoteric Knowledge**: Requires knowledge of Whitespace language
3. **Binary Encoding**: Numbers are encoded in binary within the language
4. **Filename Hint**: "They_call_me_Cutie" hints at the flag's "cutie" reference

### The Challenge Description Clues

Every hint pointed toward the solution:

- **"hidden not in what is written"** → Ignore the visible S/T/L, focus on what they represent
- **"read between the lines"** → Whitespace between visible characters (literally!)
- **"Don't trust me I am Lier"** → Odd capitalization and spelling hint at S/T/L
- **"The sea doesn't shout its secrets"** → Silent/invisible (whitespace)

## Learning Outcomes

### Concepts Demonstrated

1. **Esoteric Programming Languages**: Understanding unusual language designs
2. **Binary Encoding**: Converting binary to decimal to ASCII
3. **Steganography**: Data hidden in plain sight (whitespace)
4. **Pattern Recognition**: Identifying structure in seemingly random data
5. **File Format Analysis**: Understanding how data can be encoded

### Skills Practiced

- Reading programming language specifications
- Binary arithmetic and conversion
- Character encoding (ASCII)
- File parsing and text processing
- Automated decoding script writing

## Alternative Solutions

### Using Online Tools

1. **Whitespace Interpreter**:
   - Convert S→Space, T→Tab, L→LineFeed
   - Run in online interpreter
   - Watch output

2. **CyberChef Recipe**:
   ```
   Find/Replace (S → Space)
   Find/Replace (T → Tab)  
   Find/Replace (L → \n)
   Whitespace Interpreter
   ```

### Manual Decoding Table

| Char | Binary | Decimal | ASCII |
|------|--------|---------|-------|
| B | 1000010 | 66 | B |
| Y | 1011001 | 89 | Y |
| P | 1010000 | 80 | P |
| A | 1000001 | 65 | A |
| S | 1010011 | 83 | S |
| S | 1010011 | 83 | S |
| _ | 1011111 | 95 | _ |
| ... | ... | ... | ... |

## Real-World Applications

### Where Whitespace Steganography is Used

1. **Data Exfiltration**: Hiding data in document formatting
2. **Code Comments**: Secret messages in source code whitespace
3. **Trailing Spaces**: Messages in line endings
4. **Tab vs Space Wars**: Secret data in indentation choices

### Detection Techniques

```python
# Detect suspicious whitespace patterns
def analyze_whitespace(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()
    
    spaces = content.count(b' ')
    tabs = content.count(b'\t')
    linefeeds = content.count(b'\n')
    
    print(f"Spaces: {spaces}")
    print(f"Tabs: {tabs}")
    print(f"Linefeeds: {linefeeds}")
    
    # High tab/space ratio might indicate Whitespace code
    if tabs > 0 and spaces / tabs > 10:
        print("⚠️ Possible Whitespace code detected!")
```

## Resources & Tools

### Whitespace Language

- **Specification**: https://web.archive.org/web/20150618184706/http://compsoc.dur.ac.uk/whitespace/tutorial.php
- **Online Interpreter**: https://vii5ard.github.io/whitespace/
- **GitHub Implementations**: Search for "whitespace interpreter"

### ASCII Reference

- **Printable ASCII**: 32-126
- **Common characters**:
  - 'A' = 65
  - 'a' = 97
  - '0' = 48
  - Space = 32

### Binary Conversion

```python
# Binary to decimal
decimal = int('1000010', 2)  # 66

# Decimal to ASCII
char = chr(66)  # 'B'

# Combined
char = chr(int('1000010', 2))  # 'B'
```

## Difficulty Rating

**Medium** - This challenge requires:

**Why Medium:**
- Requires knowledge of esoteric programming languages
- Not obvious that it's Whitespace code
- Need to understand binary encoding
- Must write custom parser or use obscure tools

**What makes it accessible:**
- File format is consistent and structured
- Each character is independently encoded
- Binary conversion is straightforward
- Clear patterns once you understand the format

**Perfect for:**
- Learning about esoteric languages
- Practicing binary/ASCII conversion
- Understanding alternative encoding methods
- Introduction to steganography concepts

## Conclusion

"Whispers of Cursed Soul" is an excellent challenge that teaches about esoteric programming languages and creative data hiding. The use of Whitespace is particularly clever because:

1. **Historical Significance**: Whitespace is a famous esoteric language
2. **Steganographic Potential**: Real whitespace is invisible
3. **Educational Value**: Teaches binary encoding and ASCII
4. **Thematic Fit**: "Whispers" and "hidden" perfectly describe invisible code

### Key Lessons

1. **Look Beyond the Obvious**: The visible S/T/L are markers, not the message
2. **Understand Encoding**: Data can be hidden in many ways
3. **Research is Key**: Knowing about Whitespace language is crucial
4. **Pattern Recognition**: Identifying structure leads to solutions
5. **Automation Helps**: Write scripts to handle repetitive decoding

### The Challenge's Wisdom

The description's warnings were perfect:
- **"Read between the lines"** → Literally whitespace between characters
- **"Hidden not in what is written"** → The S/T/L are just representations
- **"Don't trust me I am Lier"** → Trust the whitespace, not the visible text

The flag's message—"Whitespace cutie it was"—confirms our solution and acknowledges both the programming language and the cute misdirection of the challenge.

### Final Thoughts

This challenge demonstrates that in security and CTFs, sometimes the most important information is what you **can't see**. Just as pirates whispered their secrets rather than shouting them, this challenge hides its treasure in the silent spaces between the noise.

Remember: **The most powerful messages are often the quietest.** ☠️⚓

🏴‍☠️ The curse has been lifted, and the whispered secret revealed! ⚓
