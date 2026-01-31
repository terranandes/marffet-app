import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


import sys
import os
from pathlib import Path
from fastapi import Request
from starlette.datastructures import Headers

# Verify we can import config
try:
    from app.main import COOKIE_DOMAIN
    print(f"SUCCESS: Imported COOKIE_DOMAIN: {COOKIE_DOMAIN}")
except ImportError as e:
    print(f"FAIL: Could not import COOKIE_DOMAIN: {e}")
except Exception as e:
    print(f"FAIL: Unexpected error importing COOKIE_DOMAIN: {e}")

# Now try to import auth and call logout
try:
    from app.auth import logout
    print("SUCCESS: Imported logout function")
except ImportError as e:
    print(f"FAIL: Could not import logout: {e}")
    sys.exit(1)

# Mock Request
async def run_test():
    print("Running logout test...")
    scope = {
        'type': 'http',
        'headers': [[b'accept', b'application/json']],
        'session': {'user': 'test'},
    }
    
    # We need a partial mock of Request
    class MockRequest:
        def __init__(self):
            self.headers = Headers({'accept': 'application/json'})
            self.session = {'user': 'test'}
            self.base_url = "https://martian-api.zeabur.app"
            # dict has clear() built-in, no need to mock logic unless we spy on it
            # self.session.clear is fine

    req = MockRequest()
    
    try:
        response = await logout(req)
        print("SUCCESS: Logout executed without error")
        print(f"Response status: {response.status_code}")
        # Verify cookies
        # JSONResponse doesn't expose set-cookie easily in raw form without rendering
        # but if it didn't crash, the import worked.
    except Exception as e:
        print(f"FAIL: Logout raised error: {e}")
        import traceback
        traceback.print_exc()

import asyncio
asyncio.run(run_test())
