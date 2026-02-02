
import os
import requests
from datetime import datetime, timezone, timedelta

def debug_check():
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPO")
    
    print(f"Token: {'Set' if token else 'Missing'}")
    print(f"Repo: {repo}")

    if not token or not repo:
        return
        
    try:
        target_path = "app/portfolio.db"
        # Mirror exact logic
        url = f"https://api.github.com/repos/{repo}/commits?path={target_path}&per_page=1"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
        
        print(f"Fetching: {url}")
        resp = requests.get(url, headers=headers)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            commits = resp.json()
            if commits and len(commits) > 0:
                last_date_str = commits[0]["commit"]["committer"]["date"]
                print(f"Last Commit Date (Str): {last_date_str}")
                
                last_backup_time = datetime.fromisoformat(last_date_str.replace("Z", "+00:00"))
                print(f"Last Backup Time (Obj): {last_backup_time}")
                
                now = datetime.now(timezone.utc)
                print(f"Now (UTC): {now}")
                
                age = now - last_backup_time
                print(f"Age: {age}")
                print(f"Age Hours: {age.total_seconds() / 3600}")
                
                if age > timedelta(hours=20):
                    print("Result: STALE (>20h). Would trigger backup.")
                else:
                    print("Result: FRESH. Would skip.")
            else:
                print("Result: No commits found.")
        else:
            print(f"Result: API Error {resp.text}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    debug_check()
