
from html.parser import HTMLParser

class NestingChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.app_open = False
        self.app_closed_at = None
        self.script_start = None
        self.line_no = 0

    def handle_starttag(self, tag, attrs):
        if tag in ['br', 'img', 'input', 'hr', 'meta', 'link']:
            return
        
        # Check for id="app"
        addr_dict = dict(attrs)
        if tag == 'div' and addr_dict.get('id') == 'app':
            self.app_open = True
            print(f"DEBUG: #app opened at line {self.getpos()[0]}")
        
        if self.app_open:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if not self.app_open:
            return

        if self.stack:
            last_tag, start_line = self.stack[-1]
            if last_tag == tag:
                 self.stack.pop()
                 if not self.stack:
                     print(f"DEBUG: #app closed fully at line {self.getpos()[0]}")
                     self.app_open = False
                     self.app_closed_at = self.getpos()[0]
            else:
                # Mismatch or unclosed tag (ignored for this simple check usually, but vital here)
                pass

    def handle_data(self, data):
        if "<script type=\"module\">" in data or "import {" in data:
             # Basic check if parser doesn't catch script start as tag if inside bad HTML
             pass

with open('app/static/index.html', 'r') as f:
    content = f.read()

parser = NestingChecker()
# Find script start position manually to compare
script_idx = content.find('<script type="module">')
script_line = content[:script_idx].count('\n') + 1
print(f"DEBUG: Script starts at line {script_line}")

parser.feed(content)

if parser.app_open:
    print(f"FAILURE: #app is still OPEN at EOF. Stack depth: {len(parser.stack)}")
    print(f"Unclosed tags stack (last 5): {parser.stack[-5:]}")
else:
    print(f"SUCCESS: #app closed at {parser.app_closed_at}")
    if parser.app_closed_at < script_line:
        print("VERIFIED: #app closes BEFORE script.")
    else:
        print("FAILURE: #app closes AFTER script starts.")
