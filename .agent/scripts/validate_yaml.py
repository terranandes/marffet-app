import os
import re

dir_path = "/home/terwu01/github/marffet/.agent/skills"

for root, _, files in os.walk(dir_path):
    for file in files:
        if file.endswith(".md"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    
                match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
                if match:
                    yaml_str = match.group(1)
                    # Check for common yaml syntax errors manually without external yaml library
                    lines = yaml_str.split('\n')
                    for i, line in enumerate(lines):
                        if ':' in line:
                            key, val = line.split(':', 1)
                            val = val.strip()
                            # If value contains unescaped special characters without quotes
                            if len(val) > 0 and val[0] not in ["'", '"', '[', '{']:
                                if ':' in val:
                                    print(f"[{filepath}] Error: Unquoted colon in value '{val}' (line {i+1} of frontmatter: {line})")
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
