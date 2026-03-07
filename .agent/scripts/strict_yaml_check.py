import os
import re
import yaml
import sys

def check_dir(dir_path):
    if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
        return
    print(f"Checking {dir_path}...")
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
                            # Use pyyaml to parse strictly
                            yaml.safe_load(yaml_str)
                        except yaml.YAMLError as exc:
                            print(f"\nCRITICAL YAML ERROR in {filepath}:")
                            print(exc)
                            print(f"Frontmatter content:\n{yaml_str}\n")
                    else:
                        # Some might missing frontmatter, we can just warn
                        pass
                except Exception as e:
                    print(f"Could not read {filepath}: {e}")

check_dir("/home/terwu01/github/marffet/.agent/workflows")
check_dir("/home/terwu01/github/marffet/.agent/skills")
check_dir("/home/terwu01/.gemini/skills")
check_dir("/home/terwu01/.gemini/commands")
