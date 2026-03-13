import os
import json
import sys

# Define where to save the state
state_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".worktrees", "auth_states", "state_gm.json"))
os.makedirs(os.path.dirname(state_file), exist_ok=True)

print("Let's manually create the auth state.")
print("1. Please open your normal Google Chrome browser.")
print("2. Navigate to https://marffet-app.zeabur.app and log in with terranfund@gmail.com.")
print("3. Once you see the Portfolio page, Right Click -> Inspect to open DevTools.")
print("4. Go to the Application tab -> Cookies -> https://marffet-app.zeabur.app.")
print("5. Find the cookie named 'session' and copy its entire Value.")
print("-" * 50)
session_val = input("Paste the 'session' cookie value here: ").strip()

state_json = {
  "cookies": [
    {
      "name": "session",
      "value": session_val,
      "domain": "marffet-api.zeabur.app",
      "path": "/",
      "expires": -1,
      "httpOnly": True,
      "secure": True,
      "sameSite": "Lax"
    }
  ],
  "origins": []
}

with open(state_file, 'w') as f:
    json.dump(state_json, f, indent=2)

print(f"\n✅ State successfully written to: {state_file}")
print("You can now run the tests!")
