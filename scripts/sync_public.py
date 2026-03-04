import os

src_dir = "/home/terwu01/github/marffet"
target_dir = "/home/terwu01/github/marffet-app"

# Clean up previously wrongly copied files/folders in marffet-app
os.system(f"rm -rf {target_dir}/docs")

# Create target directories
os.makedirs(os.path.join(target_dir, "frontend/public/images"), exist_ok=True)

# Function to copy and adjust image paths for the root READMEs
def copy_and_adjust_paths(src_file, dst_file):
    with open(src_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # In the private repo, these files live in docs/product/ so they reference ../../frontend
    # In the public repo, they will live in the root, so they should reference frontend
    content = content.replace('src="../../frontend/', 'src="frontend/')
    
    with open(dst_file, 'w', encoding='utf-8') as f:
        f.write(content)

# Copy images via system command (simplest)
os.system(f"cp {src_dir}/frontend/public/images/bmc-yellow-button.png {target_dir}/frontend/public/images/bmc-yellow-button.png")
os.system(f"cp {src_dir}/frontend/public/images/kofi-blue-button.png {target_dir}/frontend/public/images/kofi-blue-button.png")

# Copy the End-User READMEs from docs/product/ to the ROOT of marffet-app
copy_and_adjust_paths(os.path.join(src_dir, "docs/product/README.md"), os.path.join(target_dir, "README.md"))
copy_and_adjust_paths(os.path.join(src_dir, "docs/product/README-zh-TW.md"), os.path.join(target_dir, "README-zh-TW.md"))
copy_and_adjust_paths(os.path.join(src_dir, "docs/product/README-zh-CN.md"), os.path.join(target_dir, "README-zh-CN.md"))

print("Public Showcase sync executed successfully! Roots deployed properly.")
