import shutil
import os

path = "/home/terwu01/github/marffet/.agent/workflows/gemini-cli"
if os.path.exists(path):
    shutil.rmtree(path)
    print("Deleted gemini-cli directory")
else:
    print("Directory does not exist")
