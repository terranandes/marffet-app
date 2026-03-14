import os

base = "/home/terwu01/github/marffet/.gemini"
for link_name in ["skills", "commands"]:
    path = os.path.join(base, link_name)
    if os.path.islink(path):
        target = os.readlink(path)
        real_target = os.path.join(base, target)
        exists = os.path.exists(path)
        print(f"{link_name} -> {target} (exists: {exists})")
        if not exists:
            print(f"  Broken symlink! {real_target} does not exist.")
    elif os.path.exists(path):
        print(f"{link_name} is a normal directory/file.")
    else:
        print(f"{link_name} does not exist at all.")
