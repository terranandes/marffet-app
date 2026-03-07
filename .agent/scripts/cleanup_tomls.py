import os

workflow_dir = "/home/terwu01/github/marffet/.agent/workflows"

deleted_count = 0
for filename in os.listdir(workflow_dir):
    if filename.endswith(".toml"):
        file_path = os.path.join(workflow_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted: {filename}")
            deleted_count += 1

print(f"Deleted {deleted_count} .toml files from {workflow_dir}")
