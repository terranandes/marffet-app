import os
import shutil

workflow_dir = "/home/terwu01/github/marffet/.agent/workflows"
dest_dir = os.path.join(workflow_dir, "gemini-cli")

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

moved_count = 0
for filename in os.listdir(workflow_dir):
    if filename.endswith(".toml"):
        src = os.path.join(workflow_dir, filename)
        dst = os.path.join(dest_dir, filename)
        shutil.move(src, dst)
        print(f"Moved: {filename}")
        moved_count += 1

print(f"Moved {moved_count} .toml files to {dest_dir}")
