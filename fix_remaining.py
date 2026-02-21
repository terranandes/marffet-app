import re
from pathlib import Path

def apply_fixes(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    out = []
    for line in lines:
        if 'except:' in line and 'except Exception:' not in line:
            line = line.replace('except:', 'except Exception:')
            
        m = re.match(r"^(\s*)if (.+?):\s*return\s*(.+)$", line)
        if m:
            indent, cond, ret = m.groups()
            line = f"{indent}if {cond}:\n{indent}    return {ret.strip()}\n"
            
        m = re.match(r"^(\s*)if (.+?):\s*continue\s*(\#.*)?\n$", line)
        if m:
            indent, cond, comment = m.groups()
            comment_str = comment if comment else ""
            line = f"{indent}if {cond}:\n{indent}    continue {comment_str}\n"

        m = re.match(r"^(\s*)if (.+?):\s*break\s*(\#.*)?\n$", line)
        if m:
            indent, cond, comment = m.groups()
            comment_str = comment if comment else ""
            line = f"{indent}if {cond}:\n{indent}    break {comment_str}\n"

        m = re.match(r"^(\s*)except Exception:\s*pass\s*\n$", line)
        if m:
            indent = m.group(1)
            line = f"{indent}except Exception:\n{indent}    pass\n"
            
        out.append(line)
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(out)

for p in Path('app').rglob('*.py'):
    apply_fixes(p)
    
