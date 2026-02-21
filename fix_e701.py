import subprocess
import os
from pathlib import Path

result = subprocess.run(["uv", "run", "ruff", "check", "app/"], capture_output=True, text=True)
lines = result.stdout.splitlines()

target_files = set()
for line in lines:
    if 'E701' in line or 'E722' in line:
        pass # Just look at the next line for filename
    elif line.startswith('  --> '):
        file_path = line.split('--> ')[1].split(':')[0]
        target_files.add(file_path)

import autopep8
for f in target_files:
    if not os.path.exists(f): continue
    with open(f, 'r', encoding='utf-8') as file:
        code = file.read()
    
    # autopep8 handles these cleanly without destroying the file if used correctly
    fixed = autopep8.fix_code(code, options={'select': ['E701', 'E722'], 'aggressive': 1})
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(fixed)

print(f"Ran autopep8 on {len(target_files)} files.")
