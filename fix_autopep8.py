import autopep8
from pathlib import Path

for pcls in Path('app').rglob('*.py'):
    with open(pcls, 'r', encoding='utf-8') as iter_f:
        content = iter_f.read()
        
    fixed = autopep8.fix_code(content, options={'select': ['E701', 'E722']})
    
    with open(pcls, 'w', encoding='utf-8') as w_f:
        w_f.write(fixed)
