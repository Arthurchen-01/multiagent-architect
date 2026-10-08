with open(r'C:\Users\s990uma\.gemini\antigravity\brain\e227c0d2-f4ee-4869-93fd-41240442eb4d\.system_generated\steps\253\content.md', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re
pag = re.findall(r'href="([^"]+after=[^"]+)"', text)
print("PAGINATION:", pag)

next_btn = re.findall(r'<a[^>]+>Next</a>', text, re.IGNORECASE)
print("NEXT BTN:", next_btn)
