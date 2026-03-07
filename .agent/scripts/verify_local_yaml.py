import os
import re
import yaml

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
                        content = f.read()
                    
                    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
                    if match:
                        yaml_str = match.group(1)
                        try:
                            # strict parse
                            yaml.safe_load(yaml_str)
                        except yaml.YAMLError as exc:
                            print(f"\n[X] CRITICAL YAML ERROR in {filepath}:")
                            print(exc)
                            error_count += 1
                except Exception as e:
                    print(f"Could not read {filepath}: {e}")
    if error_count == 0:
        print(f"All good in {dir_path}!")

check_dir("/home/terwu01/github/marffet/.agent/workflows")
check_dir("/home/terwu01/github/marffet/.agent/skills")
