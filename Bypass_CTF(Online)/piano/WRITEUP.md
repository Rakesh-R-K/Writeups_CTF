# Bypass CTF writeup : Piano Steganography CTF Challenge 

## Challenge Description
*"They said the melody was cursed... a tune played by a mad pirate who hid his treasure in sound itself. Listen close, sailor. The chords you hear aren't random — they spell the name of his lost ship. Find the word, claim the flag, and pray Davy Jones doesn't find you first."*

**Given File:** `pirate_song.mp3`

## Solution

### Analysis Approach
This is an audio steganography challenge where the hidden message is encoded in the musical notes themselves. The challenge hint suggests that the "chords" spell out the name of the pirate's lost ship.

### Tools Used
- Python with librosa (audio analysis library)
- scipy, numpy, matplotlib for signal processing

### Step-by-Step Solution

1. **Load the audio file** using librosa to analyze its musical content
2. **Detect note onsets** to identify when each note is played
3. **Extract chromagram** to determine which musical notes are present
4. **Map dominant notes** at each onset point to their letter names

### Key Insight
Musical notes are named using letters: **A, B, C, D, E, F, G** (and their sharps/flats). The challenge cleverly uses this property to encode a message directly in the melody.

### Extracted Notes Sequence

| Note # | Time (s) | Musical Note |
|--------|----------|--------------|
| 1      | 1.26     | B            |
| 2      | 2.15     | A            |
| 3      | 3.38     | D            |
| 4      | 4.80     | F            |
| 5      | 5.76     | A            |
| 6      | 6.82     | C            |
| 7      | 7.84     | E            |

Reading the notes in sequence: **B - A - D - F - A - C - E**

### Flag
**BADFACE**

This is the name of the pirate's "lost ship" hidden in the melody!

## Python Analysis Code
```python
import librosa

# Load audio file
y, sr = librosa.load("pirate_song.mp3", sr=None)

# Detect note onsets
onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
onset_times = librosa.frames_to_time(onset_frames, sr=sr)

# Extract chromagram (which notes are played)
chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

# Get dominant note at each onset
note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
notes_sequence = []

for onset_time in onset_times:
    frame = librosa.time_to_frames(onset_time, sr=sr)
    if frame < chroma.shape[1]:
        chroma_vals = chroma[:, frame]
        dominant_note_idx = np.argmax(chroma_vals)
        note = note_names[dominant_note_idx]
        notes_sequence.append(note)

# Extract flag
flag = ''.join([n[0] for n in notes_sequence])
print(f"Flag: {flag}")  # Output: BADFACE
```

## Lessons Learned
- Audio steganography can hide messages in the actual musical content, not just metadata
- Musical note names (A-G) can be used to encode alphabetic messages
- Librosa is an excellent library for musical/audio analysis in Python
- Chromagram analysis reveals which musical notes are present in audio over time

