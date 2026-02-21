import re

with open('.agent/skills/lint-and-validate/scripts/lint_runner.py', 'r') as f:
    content = f.read()

# Change mypy target from app to "." to avoid the nested app.project_tw vs project_tw collision
content = content.replace('"cmd": ["mypy", "app"]', '"cmd": ["mypy", ".", "--exclude", "tests/", "--exclude", "tests_gemini/", "--exclude", "\.agent/", "--exclude", "\.agents/"]')
with open('.agent/skills/lint-and-validate/scripts/lint_runner.py', 'w') as f:
    f.write(content)

