# Challenge: Hijack

## Challenge Description
This challenge involves analyzing a web application to find a hidden flag. The challenge name "Hijack" suggests it may involve clickjacking, session hijacking, or other web security vulnerabilities.

**Given:** Web application URL

## Solution

### Initial Analysis
Upon accessing the challenge website, the application appears to be a standard web interface. The challenge requires investigating the source code and resources loaded by the webpage to find the flag.

### Investigation Process

#### Step 1: Inspect Page Source
The first step in web-based CTF challenges is to inspect the page source. Modern web applications often use bundled and minified JavaScript files that may contain interesting information.

#### Step 2: Examine JavaScript Files
Looking at the network requests or page resources, we can identify the JavaScript files being loaded. In this case, there's a file named `index-6720897b.js` which appears to be a React application bundle.

#### Step 3: Search the Source Code
Since the JavaScript is minified, we need to search through it carefully. Common approaches include:
- Searching for common flag patterns like `enigmaCTF26{`
- Looking for base64 encoded strings
- Examining any configuration objects or constants
- Checking for commented-out code

#### Step 4: Finding the Flag
By searching through the JavaScript source code (either by viewing the source directly or using browser DevTools), the flag can be found embedded in the minified code:

```
enigmaCTF26{pr351d3n7_bu5h_w0uldn7_b3_h4ppy_b0u7_7h15_8375}
```

### Flag Location
The flag was found directly in the JavaScript source code, likely in:
- The `index-6720897b.js` file
- Embedded as a string literal or configuration value
- Possibly in a React component or application state

### Why This Works
Web applications often include:
- Debugging code or test data that wasn't removed before deployment
- Configuration values embedded in client-side JavaScript
- Flags intentionally placed for CTF challenges in accessible locations
- Source maps or unminified code accidentally deployed

## Flag
`enigmaCTF26{pr351d3n7_bu5h_w0uldn7_b3_h4ppy_b0u7_7h15_8375}`

## Key Takeaways
- **Always inspect the source**: Client-side code is fully visible to anyone who accesses the website
- **Check all loaded resources**: JavaScript bundles, CSS files, and other assets may contain sensitive information
- **Use browser DevTools**: The Network tab, Sources panel, and Console are essential for web challenges
- **Search strategically**: Look for flag patterns, base64 strings, and unusual text
- **Client-side security is an illusion**: Never store sensitive information (like flags, API keys, or secrets) in client-side code
- The flag reference to "president bush" and "wouldn't be happy about this" is likely a nod to security vulnerabilities or the importance of not exposing sensitive information in client-side code
- This challenge demonstrates why proper code review and sanitization before deployment is crucial

## Tools Used
- Browser Developer Tools (Chrome/Firefox DevTools)
- View Page Source functionality
- Text search (Ctrl+F) to find flag patterns
