
import os
import re

SKILLS_DIR = "/home/terwu01/.gemini/antigravity/global_skills"

# Replacements (Order matters for overlapping strings)
SIMPLE_REPLACEMENTS = [
    # Global Config / Paths
    ("CLAUDE.md", "GEMINI.md"),
    ("~/.claude/skills/", "~/.gemini/antigravity/global_skills/"),
    (".claude/skills/", ".gemini/antigravity/global_skills/"),
    ("~/.config/superpowers/", "~/.gemini/antigravity/global_skills/"),
    
    # Node / Bun
    ("npm install", "bun install"),
    ("npm ci", "bun install"),
    ("npm run", "bun run"),
    ("npm start", "bun start"),
    ("npm test", "bun test"),
    ("npx ", "bunx "),
    ("node ", "bun "), # Replaces 'node script.js' -> 'bun script.js'. Risky for text, but likely code.
    
    # Python / UV
    ("pip install", "uv pip install"),
    ("poetry install", "uv sync"),
    ("poetry run", "uv run"),
    ("python3 -m venv", "uv venv"),
    ("virtualenv venv", "uv venv"),
    
    # Specific Tool Commands
    ("npx create-next-app", "bun create next-app"),
    ("npx create-react-app", "bun create react-app"),
    ("npx create-vite", "bun create vite"),
]

def update_content(content):
    original = content
    
    # 1. Apply simple string replacements
    for old, new in SIMPLE_REPLACEMENTS:
        content = content.replace(old, new)
        
    # 2. Regex for Announcement
    # Old: **Announce at start:** "I'm using the foo skill..."
    # New: **Announce at start:** "Applying knowledge of `foo`..."
    announcement_pattern = r'\*\*Announce at start:\*\* "(?:I\'m using the|Applying knowledge of) ([a-zA-Z0-9-_]+)(?: skill)?.*?"'
    
    def repl(m):
        skill_name = m.group(1)
        return f'**Announce at start:** "Applying knowledge of `{skill_name}`..."'
        
    content = re.sub(announcement_pattern, repl, content)
    
    # 3. Special case: Fix "bun pip install" if someone chained replacements poorly (not happening here due to direct strings)
    # But "uv pip install" is correct.
    
    # 4. Check for setup blocks (like in using-git-worktrees)
    # If we see the old block, replace it with the smart block.
    # This is a bit specific, but high value if found.
    
    old_setup_block = """# Node.js
if [ -f package.json ]; then npm install; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Python
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then poetry install; fi

# Go
if [ -f go.mod ]; then go mod download; fi"""

    new_setup_block = """# Node.js / TypeScript (Uses bun)
if [ -f package.json ] || [ -f bun.lockb ]; then bun install; fi

# Python (Uses uv)
if [ -f pyproject.toml ]; then uv sync; fi
if [ -f requirements.txt ]; then uv pip install -r requirements.txt; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Go
if [ -f go.mod ]; then go mod download; fi"""
    
    # Normalize whitespace for block replacement
    # (Actually, better to relies on the component lines if exact block match fails)
    if old_setup_block in original: # Check original to avoid partial replacement issues
        content = content.replace(old_setup_block, new_setup_block)
        # Fix potential double replacement if simple replacements already touched the block in `content`
        # Since I replaced `content` already, `npm install` is `bun install` in `content`.
        # So exact match on `old_setup_block` (which has `npm`) against `content` (which has `bun`) will fail.
        # So I should check against `original` but applying to `content` is hard if `content` changed.
        # Strategy: Use a dedicated substitution for this block that runs BEFORE simple replacements?
        pass

    return content

def smart_block_replacement(content):
    # This block usually appears in `using-git-worktrees` or similar implementation skills.
    # The simple replacements might have already mangled it (npm -> bun).
    # So let's construct what the "mangled" old block looks like after simple replacements.
    
    mangled_old_block = """# Node.js
if [ -f package.json ]; then bun install; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Python
if [ -f requirements.txt ]; then uv pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then uv sync; fi

# Go
if [ -f go.mod ]; then go mod download; fi"""

    new_setup_block = """# Node.js / TypeScript (Uses bun)
if [ -f package.json ] || [ -f bun.lockb ]; then bun install; fi

# Python (Uses uv)
if [ -f pyproject.toml ]; then uv sync; fi
if [ -f requirements.txt ]; then uv pip install -r requirements.txt; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Go
if [ -f go.mod ]; then go mod download; fi"""

    # Try replacing the mangled version
    if mangled_old_block in content:
        content = content.replace(mangled_old_block, new_setup_block)
        return content
        
    # Also try replacing the original version in case simple replacements didn't run yet (but they did)
    # Or if formatting slightly differs.
    
    return content

def process_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        new_content = update_content(content)
        new_content = smart_block_replacement(new_content)
        
        if content != new_content:
            print(f"Migrating {file_path}")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
                
    except UnicodeDecodeError:
        print(f"Skipping binary file: {file_path}")

def main():
    print(f"Scanning {SKILLS_DIR}...")
    for root, dirs, files in os.walk(SKILLS_DIR):
        for file in files:
            if file.endswith((".md", ".py", ".sh")): # Process Markdown and Script files
                process_file(os.path.join(root, file))
    print("Migration complete.")

if __name__ == "__main__":
    main()
