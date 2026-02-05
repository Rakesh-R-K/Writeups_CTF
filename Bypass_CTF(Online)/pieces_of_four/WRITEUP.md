# Bypass CTF Challenge Writeup : Pieces of Four 

## Challenge Description
```
Legends speak of a cursed chest recovered from the depths of the Caribbean.
Every pirate who opens it swears they see something different —
a torn map fragment, a broken sigil, or a piece of a greater truth. - 44442
```

**File provided:** `piece_of_four`

## Solution

### Step 1: Initial Analysis
First, I examined the file's magic bytes:
```bash
First 4 bytes: F0 D0 FF E0
```

The file appeared to be a corrupted JPEG (notice "JFIF" in the header), but the magic bytes were wrong. Standard JPEG files start with `FF D8 FF E0`, but this had `F0 D0 FF E0`.

### Step 2: String Analysis
Searching for embedded content revealed something interesting:
```bash
strings piece_of_four
```

This revealed an embedded SVG file containing a base64-encoded PNG image within the JPEG data.

### Step 3: Extract the Hidden PNG
The key was extracting the base64-encoded PNG from the SVG data embedded in the file:

```powershell
$content = Get-Content piece_of_four -Raw
$pattern = 'data:image/png;base64,([^"]+)'
if($content -match $pattern) {
    $base64 = $matches[1]
    $bytes = [System.Convert]::FromBase64String($base64)
    [System.IO.File]::WriteAllBytes("extracted.png", $bytes)
}
```

### Step 4: Scan the PNG
The extracted PNG image (`extracted.png`) contains the flag. Scanning it (likely with a QR code reader or similar tool) reveals the flag.

### FLAG:
BYPASS_CTF{JPEG_PNG_GIF_TIFF_c0mm0n}

## Key Insights
- The challenge name "pieces of four" and the hint "44442" suggested multiple embedded components
- The corrupted JPEG magic bytes were a red herring - the real treasure was the embedded PNG
- SVG files can contain base64-encoded images inline, which is how the PNG was hidden
- Don't get distracted by fixing the JPEG - the flag wasn't in the image itself but in the hidden data

## Files Generated
- `extracted.png` - The hidden PNG containing the flag (scan this for the flag)
