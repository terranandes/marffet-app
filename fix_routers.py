import re

with open('app/main.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.strip() == "from app.project_tw.strategies.cb import CBStrategy":
        pass
    else:
        new_lines.append(line)

content = "".join(new_lines)
with open('app/main.py', 'w') as f:
    f.write(content)
