import os
import subprocess

def run_cmd(cmd):
    print(f"--- Running: {cmd} ---")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("ERROR:", result.stderr)
    except Exception as e:
        print("EXCEPTION:", str(e))
    print()

run_cmd("ls -la ~/.gemini")
run_cmd("ls -la ~/.gemini/commands")
run_cmd("ls -la ~/.gemini/skills")
run_cmd("ls -la ~/.gemini/antigravity")
run_cmd("ls -la ~/.gemini/antigravity/global_workflows")
