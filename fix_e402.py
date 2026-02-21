import re

with open('app/main.py', 'r') as f:
    lines = f.readlines()

imports_to_move = []
clean_lines = []

for line in lines:
    if line.startswith("import time") or line.startswith("from urllib.parse import urlparse") or line.startswith("from fastapi.responses import StreamingResponse") or line.startswith("from app.feedback_db import") or "submit_feedback" in line or "get_feedback_stats" in line or line.strip() == ")":
        # Keep them but we will move them to top
        if line.startswith("from ") or line.startswith("import "):
            imports_to_move.append(line)
        # We manually just prepend these to file top, and drop them from here
        if "feedback_db" in line or "submit_feedback" in line or "get_feedback_stats" in line or line.strip() == ")":
            pass # drop multiline import string
    else:
        clean_lines.append(line)

imports_block = """
import time
from urllib.parse import urlparse
from fastapi.responses import StreamingResponse
from app.feedback_db import (
    submit_feedback, get_all_feedback, update_feedback, 
    get_feedback_stats, get_feature_categories
)
"""

new_content = imports_block + "".join(clean_lines)

with open('app/main.py', 'w') as f:
    f.write(new_content)

