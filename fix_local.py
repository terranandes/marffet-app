from pathlib import Path

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    out = []
    for line in lines:
        if 'if not user: raise HTTPException' in line:
            indent = line[:len(line) - len(line.lstrip())]
            rest = line.split('raise ', 1)[1].strip()
            line = f"{indent}if not user:\n{indent}    raise {rest}\n"
        out.append(line)
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(out)

fix_file("app/routers/portfolio.py")
