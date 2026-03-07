import os
base = "/home/terwu01/.gemini"
for link_name in ["skills", "commands"]:
    path = os.path.join(base, link_name)
    if os.path.islink(path):
        target = os.readlink(path)
        real_target = os.path.join(base, target) if not target.startswith('/') else target
        print(f"{link_name} -> {target} (exists: {os.path.exists(path)})")
    elif os.path.exists(path):
        print(f"{link_name} is a normal file/dir.")
    else:
        print(f"{link_name} does not exist.")
