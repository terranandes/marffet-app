import os
import re

def check_dir(dir_path):
    if not os.path.exists(dir_path):
        return
    print(f"Scanning {dir_path}...")
    error_count = 0
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    if not lines:
                        continue
                        
                    first_line = lines[0].strip()
                    if first_line != '---':
                        # This file lacks frontmatter completely
                        print(f"[!] WARNING: Missing frontmatter in {filepath}")
                        continue
                        
                    # Find closing ---
                    end_idx = -1
                    for i in range(1, len(lines)):
                        if lines[i].strip() == '---':
                            end_idx = i
                            break
                            
                    if end_idx == -1:
                        print(f"\n[X] CRITICAL ERROR in {filepath}: Unclosed frontmatter (missing '---')")
                        error_count += 1
                        continue
                        
                    # Now check inside the frontmatter for basic syntax
                    yaml_lines = lines[1:end_idx]
                    for i, line in enumerate(yaml_lines):
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                            
                        # Must have a colon
                        if ':' not in line:
                            print(f"\n[X] CRITICAL ERROR in {filepath} (line {i+2}): Missing colon in YAML block -> {line}")
                            error_count += 1
                            continue
                            
                        # Split by first colon
                        key, val = line.split(':', 1)
                        val = val.strip()
                        
                        # Grey matter strictly requires quotes if the string contains a colon or starts with certain chars
                        if val:
                            first_char = val[0]
                            is_quoted = (first_char == '"' and val.endswith('"')) or (first_char == "'" and val.endswith("'"))
                            
                            if not is_quoted:
                                # If it's not quoted, there cannot be ANY unescaped colons inside the value itself in strict YAML
                                if ':' in val:
                                    # Wait, URL like http:// is an exception in some parsers, but grey-matter often chokes on unquoted colons
                                    if "http://" not in val and "https://" not in val:
                                        print(f"\n[X] CRITICAL ERROR in {filepath} (line {i+2}): Unquoted value contains a colon -> {line}")
                                        error_count += 1
                                        continue
                                        
                                # Cannot start with [ or { if it's meant to be a string
                                if first_char in ['[', '{', '@', '`']:
                                    print(f"\n[X] CRITICAL ERROR in {filepath} (line {i+2}): Unquoted value starts with special char '{first_char}' -> {line}")
                                    error_count += 1
                                    continue
                                    
                except Exception as e:
                    print(f"Could not read {filepath}: {e}")
                    
    if error_count == 0:
        print(f"All basic syntax looks good in {dir_path}!")

check_dir("/home/terwu01/github/marffet/.agent/workflows")
check_dir("/home/terwu01/github/marffet/.agent/skills")
