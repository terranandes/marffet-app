import os

path = "/home/terwu01/github/marffet/.gemini"
if os.path.exists(path):
    for f in os.listdir(path):
        fp = os.path.join(path, f)
        if os.path.islink(fp):
            print(f"{f} -> {os.readlink(fp)}")
        else:
            print(f"{f} is not a symlink")
