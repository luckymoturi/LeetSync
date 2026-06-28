import os
import sys
import json
import time
import requests
import subprocess
from pathlib import Path

# Configuration
REPO_PATH = Path(__file__).parent.resolve()
SYNCED_FILE = REPO_PATH / ".synced.json"

# File extensions for popular languages
EXTENSIONS = {
    'python': 'py',
    'python3': 'py',
    'cpp': 'cpp',
    'java': 'java',
    'c': 'c',
    'csharp': 'cs',
    'javascript': 'js',
    'typescript': 'ts',
    'ruby': 'rb',
    'swift': 'swift',
    'golang': 'go',
    'scala': 'scala',
    'kotlin': 'kt',
    'rust': 'rs',
    'php': 'php',
}

def load_config():
    # Attempt to load from environment variables or a .env file
    # For simplicity, we just use environment variables or prompt the user.
    session = os.environ.get('LEETCODE_SESSION')
    csrf = os.environ.get('LEETCODE_CSRF_TOKEN')
    
    if not session or not csrf:
        # Check if config file exists
        config_file = REPO_PATH / "config.json"
        if config_file.exists():
            with open(config_file, "r") as f:
                config = json.load(f)
                session = config.get("LEETCODE_SESSION")
                csrf = config.get("LEETCODE_CSRF_TOKEN")
                
        if not session or not csrf:
            print("ERROR: Please set LEETCODE_SESSION and LEETCODE_CSRF_TOKEN in config.json")
            print("Example config.json:")
            print('{\n  "LEETCODE_SESSION": "your_session_cookie",\n  "LEETCODE_CSRF_TOKEN": "your_csrf_cookie"\n}')
            sys.exit(1)
            
    return session, csrf

def get_synced_ids():
    if SYNCED_FILE.exists():
        with open(SYNCED_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_synced_ids(synced_ids):
    with open(SYNCED_FILE, 'w') as f:
        json.dump(list(synced_ids), f)

def get_recent_submissions(session, csrf, limit=50):
    url = f"https://leetcode.com/api/submissions/?offset=0&limit={limit}"
    headers = {
        'Cookie': f'LEETCODE_SESSION={session}; csrftoken={csrf}',
        'x-csrftoken': csrf,
        'Referer': 'https://leetcode.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching submissions: {response.status_code} - {response.text}")
        return []
        
    data = response.json()
    return data.get('submissions_dump', [])

def get_question_tags(title_slug, session, csrf):
    url = "https://leetcode.com/graphql"
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'LEETCODE_SESSION={session}; csrftoken={csrf}',
        'x-csrftoken': csrf,
        'Referer': f'https://leetcode.com/problems/{title_slug}/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    query = """
    query questionTopicTags($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        topicTags {
          name
        }
      }
    }
    """
    
    payload = {
        "query": query,
        "variables": {"titleSlug": title_slug}
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        tags = data.get('data', {}).get('question', {}).get('topicTags', [])
        return [tag['name'] for tag in tags]
    except Exception as e:
        print(f"Error fetching tags for {title_slug}: {e}")
        return ["Uncategorized"]

def save_submission(sub, tags):
    title = sub['title']
    title_slug = sub['title_slug']
    lang = sub['lang']
    code = sub['code']
    
    # Use the first tag as the main category, or 'Uncategorized' if none
    category = tags[0] if tags else "Uncategorized"
    
    # Sanitize category and title for folder names
    safe_category = "".join([c for c in category if c.isalnum() or c in " -_"])
    safe_title = "".join([c for c in title if c.isalnum() or c in " -_"])
    
    # Create directory: Category / Problem Title
    dir_path = REPO_PATH / safe_category / safe_title
    dir_path.mkdir(parents=True, exist_ok=True)
    
    # Determine file extension
    ext = EXTENSIONS.get(lang, 'txt')
    file_path = dir_path / f"solution.{ext}"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(code)
        
    print(f"Saved: {safe_category} / {safe_title} / solution.{ext}")
    return file_path

def git_commit_and_push(file_paths, message="Sync LeetCode submission"):
    if not file_paths:
        return
        
    os.chdir(REPO_PATH)
    
    # Check if git is initialized
    if not (REPO_PATH / ".git").exists():
        subprocess.run(["git", "init"], check=True)
        print("Initialized new Git repository.")
        
    # Add files
    for path in file_paths:
        subprocess.run(["git", "add", str(path)], check=True)
        
    # Commit
    result = subprocess.run(["git", "commit", "-m", message], capture_output=True, text=True)
    if "nothing to commit" in result.stdout:
        print("Nothing new to commit.")
        return
        
    print(f"Git commit successful: {message}")
    
    # Push (only if remote is configured)
    remote_check = subprocess.run(["git", "remote"], capture_output=True, text=True)
    if remote_check.stdout.strip():
        subprocess.run(["git", "push"], check=True)
        print("Git push successful.")
    else:
        print("No Git remote configured. Skipping push. (Run 'git remote add origin <URL>' later)")

def main():
    print("Starting LeetCode Sync...")
    session, csrf = load_config()
    synced_ids = get_synced_ids()
    
    submissions = get_recent_submissions(session, csrf, limit=100)
    
    if not submissions:
        print("No submissions found or failed to fetch.")
        return
        
    new_files = []
    
    for sub in reversed(submissions): # Process oldest first to maintain history order if multiple
        sub_id = sub['id']
        
        # Only process Accepted submissions that we haven't synced yet
        if sub['status_display'] == 'Accepted' and sub_id not in synced_ids:
            title_slug = sub['title_slug']
            print(f"Processing new accepted submission: {sub['title']}")
            
            tags = get_question_tags(title_slug, session, csrf)
            
            # Save the file
            file_path = save_submission(sub, tags)
            new_files.append(file_path)
            
            # Mark as synced
            synced_ids.add(sub_id)
            save_synced_ids(synced_ids)
            
            time.sleep(1) # Be nice to LeetCode API
            
    if new_files:
        git_commit_and_push(new_files, message=f"Sync {len(new_files)} new LeetCode submissions")
    else:
        print("No new accepted submissions to sync.")

if __name__ == "__main__":
    main()
