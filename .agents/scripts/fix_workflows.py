import os
import re

workflow_dir = "/home/terwu01/github/marffet/.agent/workflows"

# Regex to find description line that IS NOT already quoted
# Matches: "description: something here"
# Does not match: "description: "something here"" or "description: 'something here'"
desc_pattern = re.compile(r'^description:\s+([^"\'\n].*)$', re.MULTILINE)

fixed_count = 0
for filename in os.listdir(workflow_dir):
    if filename.endswith(".md"):
        filepath = os.path.join(workflow_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if description exists and needs quoting
        if desc_pattern.search(content):
            new_content = desc_pattern.sub(r'description: "\1"', content)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed: {filename}")
            fixed_count += 1

print(f"Total files fixed: {fixed_count}")
