# Bypass CTF Challenge Writeup: The Captain's Session 

**Flag:** `BYPASS_CTF{My_d0g_0st3pp3d_0n_4_b33_shh}`

## Challenge Description

The challenge provides a Chrome browser profile directory with the hint:
> *"The Captain left no open tabs and no saved files. What remains is scattered within the browser itself. Track down the remnants and reveal what was hidden."*

## Solution Overview

The challenge requires finding three pieces of information from the browser profile:
1. **A bookmarked website URL** (for flag part 1)
2. **A password** (for flag part 2)
3. **A hidden message in browsing history** (for flag part 3)

## Detailed Solution

### Step 1: Analyzing the Provided Files

The challenge includes:
- `run.sh` - A script that makes HTTP POST requests to a webhook endpoint
- `Profile 1/` - A Chrome browser profile directory containing various databases

The `run.sh` script reveals the challenge structure:
- Question 1: "What is the url of the bookmarked website?"
- Question 2: "What is the password?"

### Step 2: Finding the Bookmarked Website

**File:** `Profile 1/Bookmarks`

Chrome stores bookmarks in a JSON file. Examining this file reveals:

```json
{
   "bookmark_bar": {
      "children": [ {
         "name": "ISDF-AIT",
         "type": "url",
         "url": "https://isdf.dev/"
      } ]
   }
}
```

**Answer 1:** `isdf.dev` (without protocol)

### Step 3: Finding the Password

**File:** `Profile 1/Login Data` (SQLite database)

Chrome stores saved passwords in a SQLite database. Examining the `logins` table:

```sql
SELECT * FROM logins;
```

Found entry:
- **origin_url:** `https://guess.not.work/`
- **username_value:** `answer2`
- **password_value:** (encrypted blob)

However, the password is encrypted. Checking the `password_notes` table reveals:

```sql
SELECT * FROM password_notes;
```

Result: `(1, 1, 'note', 'stepped_on', 13411216382802278, 0)`

The password note contains: **`stepped_on`**

This correlates with the browsing history showing a Google search for:
- "my dog stepped on a bee" - a famous Amber Heard meme

**Answer 2:** `stepped_on`

### Step 4: Finding the Third Flag Part

**File:** `Profile 1/History` (SQLite database)

After submitting the correct password, the response includes:
```json
{"flag_part":"_0st3pp3d_0n_","pirate_msg":"Arrr, check the history, matey!"}
```

The pirate message hints to check the browsing history. Examining the History database:

```sql
SELECT url, title FROM urls ORDER BY last_visit_time DESC;
```

Key finding:
- **URL:** `https://pastebin.com/ghPsJtUp`
- **Title:** `P3: 4_b33_shh} - Pastebin.com`

The title reveals the third part of the flag!

### Step 5: Assembling the Flag

Combining all three parts:
- Part 1: `BYPASS_CTF{My_d0g` (from bookmarked URL answer)
- Part 2: `_0st3pp3d_0n_` (from password answer)
- Part 3: `4_b33_shh}` (from browsing history)

**Complete Flag:** `BYPASS_CTF{My_d0g_0st3pp3d_0n_4_b33_shh}`

## Key Files and Tools Used

### Files Analyzed:
1. **Bookmarks** - JSON file containing bookmarked websites
2. **Login Data** - SQLite database with saved credentials
3. **History** - SQLite database with browsing history
4. **Web Data** - SQLite database (checked for additional clues)

### Tools Used:
- Python with sqlite3 module for database analysis
- JSON parsing for bookmarks
- Curl for API requests

## Additional Clues Found

The browsing history also showed multiple searches for:
- "pirates of the caribbean characters"
- "pirates of the caribbean"

These searches were red herrings designed to mislead solvers into thinking the password was a pirate character name (like "Jack Sparrow").

## Automation Script

The challenge can be solved automatically using the provided `solve3.sh` script, which:
1. Tests multiple URL format variations
2. Submits the correct answers to the webhook
3. Retrieves and displays all flag parts

```bash
bash solve3.sh
```

## Key takeaways

1. **Browser forensics** - Understanding Chrome's data storage structure
2. **SQLite analysis** - Querying browser databases for artifacts
3. **Password notes** - Chrome's password manager includes a notes feature
4. **Red herrings** - Not all clues in CTF challenges are relevant
5. **Format sensitivity** - The bookmark URL needed to be submitted without the protocol (just `isdf.dev`)

