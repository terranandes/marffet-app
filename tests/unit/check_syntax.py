import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


import re

def check_syntax(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # Extract script module
    try:
        script = content.split('<script type="module">')[1].split('</script>')[0]
    except IndexError:
        print("ERROR: Could not find <script type='module'> block")
        return

    # Check braces
    stack = []
    lines = script.split('\n')
    for i, line in enumerate(lines):
        for char in line:
            if char == '{':
                stack.append(('{', i + 1))
            elif char == '}':
                if not stack or stack[-1][0] != '{':
                    print(f"ERROR: Unmatched '}}' at line {i + 1}")
                    return
                stack.pop()
            elif char == '(':
                stack.append(('(', i + 1))
            elif char == ')':
                if not stack or stack[-1][0] != '(':
                    print(f"ERROR: Unmatched ')' at line {i + 1}")
                    return
                stack.pop()
    
    if stack:
        print(f"ERROR: Unclosed elements: {stack[-1]}")
    else:
        print("SUCCESS: Braces and parentheses are balanced.")

check_syntax('/home/terwu01/github/martian/app/static/index.html')
