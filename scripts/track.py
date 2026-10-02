import os
import json
import requests
from datetime import datetime, timezone

# Load .env file for local development (ignored in CI where env vars are injected directly)
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"), override=True)
except ImportError:
    pass  # python-dotenv not installed — that's fine in CI

GITHUB_TOKEN = os.environ.get("GH_PAT") or os.environ.get("GITHUB_TOKEN", "")
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME") or "KanishJebaMathewM"
TRACK_REPO = os.environ.get("TRACK_REPO") or "KanishJebaMathewM/Truxify"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# Debug: show which token source is active (mask the value)
_pat = os.environ.get("GH_PAT", "")
_default = os.environ.get("GITHUB_TOKEN", "")
if _pat:
    print(f"  Auth: using GH_PAT (length={len(_pat)})")
elif _default:
    print(f"  Auth: using GITHUB_TOKEN (length={len(_default)}) — may not have stargazer access")
else:
    print("  Auth: NO TOKEN found — requests will be unauthenticated")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "Github-Tracker",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"


def paginate(url):
    results = []
    page = 1
    while True:
        sep = "&" if "?" in url else "?"
        resp = requests.get(f"{url}{sep}per_page=100&page={page}", headers=HEADERS)
        if resp.status_code in (401, 403, 404):
            print(f"  Warning: {url} returned HTTP {resp.status_code}, skipping.")
            break
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        results.extend(data)
        page += 1
    return results


def get_followers():
    users = paginate(f"https://api.github.com/users/{GITHUB_USERNAME}/followers")
    return [{"username": u["login"], "avatar_url": u["avatar_url"], "html_url": u["html_url"]} for u in users]


def get_following():
    users = paginate(f"https://api.github.com/users/{GITHUB_USERNAME}/following")
    return [{"username": u["login"], "avatar_url": u["avatar_url"], "html_url": u["html_url"]} for u in users]


def get_forks():
    if not TRACK_REPO:
        return []
    forks = paginate(f"https://api.github.com/repos/{TRACK_REPO}/forks")
    return [{
        "owner": f["owner"]["login"],
        "avatar_url": f["owner"]["avatar_url"],
        "html_url": f["html_url"],
        "created_at": f["created_at"],
    } for f in forks]


def get_repo_info():
    if not TRACK_REPO:
        return {}
    try:
        resp = requests.get(f"https://api.github.com/repos/{TRACK_REPO}", headers=HEADERS)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"  Warning fetching repo info: {e}")
    return {}


def get_stargazers():
    """
    Fetch users who starred TRACK_REPO (i.e., who starred KanishJebaMathewM/Truxify).
    Requires public_repo scope on a classic PAT.
    """
    if not TRACK_REPO:
        return []
    results = []
    page = 1
    while True:
        resp = requests.get(
            f"https://api.github.com/repos/{TRACK_REPO}/stargazers?per_page=100&page={page}",
            headers=HEADERS,
        )
        if resp.status_code in (401, 403, 404):
            print(f"  Note: stargazers endpoint returned HTTP {resp.status_code}.")
            try:
                err_body = resp.json()
                print(f"  GitHub message: {err_body.get('message', 'no message')}")
            except Exception:
                pass
            return []
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        results.extend(data)
        page += 1
    return [{
        "username": s["login"],
        "avatar_url": s["avatar_url"],
        "html_url": s["html_url"],
    } for s in results]


def get_starred_repos():
    """
    Fetch repos that the authenticated user (GITHUB_USERNAME) has personally starred.
    Uses /user/starred — requires read:user or starring scope.
    """
    if not GITHUB_TOKEN:
        print("  Warning: No token — cannot fetch starred repos. Skipping.")
        return []
    results = []
    page = 1
    while True:
        resp = requests.get(
            f"https://api.github.com/user/starred?per_page=100&page={page}",
            headers=HEADERS,
        )
        if resp.status_code in (401, 403, 404):
            print(f"  Note: /user/starred returned HTTP {resp.status_code}.")
            try:
                err_body = resp.json()
                print(f"  GitHub message: {err_body.get('message', 'no message')}")
            except Exception:
                pass
            return []
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        results.extend(data)
        page += 1
    return [{
        "repo": s["full_name"],
        "owner": s["owner"]["login"],
        "avatar_url": s["owner"]["avatar_url"],
        "html_url": s["html_url"],
        "description": s.get("description") or "",
    } for s in results]


def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_json(filename, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)
    new_content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    # Only write if content changed — avoids dirty git state on no-op runs
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            existing = f.read()
        if existing == new_content:
            return  # No change, skip write
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)


def main():
    import time
    start_time = time.monotonic()
    now = datetime.now(timezone.utc).isoformat()

    # Fetch current state
    print("Fetching followers...")
    current_followers = get_followers()
    print(f"  Found {len(current_followers)} followers")

    print("Fetching following...")
    current_following = get_following()
    print(f"  Found {len(current_following)} following")

    print("Fetching forks...")
    current_forks = get_forks()
    print(f"  Found {len(current_forks)} forks")

    print("Fetching stargazers (who starred Truxify)...")
    current_stars = get_stargazers()
    api_stars_available = len(current_stars) > 0

    print("Fetching repos you've starred...")
    current_starred_repos = get_starred_repos()

    repo_info = get_repo_info()
    stars_total = repo_info.get("stargazers_count", len(current_stars))
    print(f"  Found {len(current_stars)} stargazers on {TRACK_REPO}")
    print(f"  You've personally starred {len(current_starred_repos)} repos")

    # If API returned empty (e.g. no token), preserve previously saved data
    if not api_stars_available:
        prev_stars_file = load_json("stars.json") or []
        if prev_stars_file:
            print("  Using previously saved stars.json (API unavailable)")
            current_stars = prev_stars_file

    # Load previous snapshot
    prev_snapshot = load_json("snapshot.json") or {
        "followers": [], "following": [], "forks": [], "stars": []
    }

    # Safety guard: if a fetch returned 0 results but previously had data, the API
    # likely failed silently. Abort change-detection to avoid false unfollows/unforks/unstars.
    api_ok = True
    if len(current_followers) == 0 and len(prev_snapshot.get("followers", [])) > 0:
        print("  WARNING: followers came back empty but snapshot has data — skipping change detection.")
        api_ok = False
    if len(current_following) == 0 and len(prev_snapshot.get("following", [])) > 0:
        print("  WARNING: following came back empty but snapshot has data — skipping change detection.")
        api_ok = False
    if len(current_forks) == 0 and len(prev_snapshot.get("forks", [])) > 0:
        print("  WARNING: forks came back empty but snapshot has data — skipping change detection.")
        api_ok = False
    if len(current_stars) == 0 and len(prev_snapshot.get("stars", [])) > 0:
        print("  WARNING: stars came back empty but snapshot has data — skipping change detection.")
        api_ok = False

    if not api_ok:
        print("\nAborting update — one or more API responses were empty unexpectedly.")
        print("No data files will be modified. Check token permissions and retry.")
        return

    # Compute sets
    curr_follower_names = {u["username"] for u in current_followers}
    prev_follower_names = set(prev_snapshot.get("followers", []))

    curr_following_names = {u["username"] for u in current_following}
    prev_following_names = set(prev_snapshot.get("following", []))

    curr_fork_owners = {f["owner"] for f in current_forks}
    prev_fork_owners = set(prev_snapshot.get("forks", []))

    curr_star_users = {s["username"] for s in current_stars}
    prev_star_users = set(prev_snapshot.get("stars", []))

    # Build lookup maps
    follower_map = {u["username"]: u for u in current_followers}
    following_map = {u["username"]: u for u in current_following}
    fork_map = {f["owner"]: f for f in current_forks}
    star_map = {s["username"]: s for s in current_stars}

    # Detect changes
    new_unfollowers = prev_follower_names - curr_follower_names
    new_unfollowed = prev_following_names - curr_following_names
    new_unforks = prev_fork_owners - curr_fork_owners
    new_unstars = prev_star_users - curr_star_users

    # Load historical lists
    unfollowers_history = load_json("unfollowers.json") or []
    unfollowed_history = load_json("unfollowed.json") or []
    unforks_history = load_json("unforks.json") or []
    unstars_history = load_json("unstars.json") or []

    # We need avatar info for people who left - try to get from previous data files
    prev_followers_data = load_json("followers.json") or []
    prev_following_data = load_json("following.json") or []
    prev_forks_data = load_json("forks.json") or []
    prev_stars_data = load_json("stars.json") or []

    prev_follower_map = {u["username"]: u for u in prev_followers_data}
    prev_following_map = {u["username"]: u for u in prev_following_data}
    prev_fork_map = {f["owner"]: f for f in prev_forks_data}
    prev_star_map = {s["username"]: s for s in prev_stars_data}

    # Append new unfollowers
    for username in sorted(new_unfollowers):
        info = prev_follower_map.get(username, {})
        unfollowers_history.append({
            "username": username,
            "avatar_url": info.get("avatar_url", ""),
            "html_url": info.get("html_url", f"https://github.com/{username}"),
            "date": now,
        })
        print(f"  Unfollower detected: {username}")

    # Append new unfollowed
    for username in sorted(new_unfollowed):
        info = prev_following_map.get(username, {})
        unfollowed_history.append({
            "username": username,
            "avatar_url": info.get("avatar_url", ""),
            "html_url": info.get("html_url", f"https://github.com/{username}"),
            "date": now,
        })
        print(f"  Unfollowed detected: {username}")

    # Append new unforks
    for owner in sorted(new_unforks):
        info = prev_fork_map.get(owner, {})
        unforks_history.append({
            "owner": owner,
            "avatar_url": info.get("avatar_url", ""),
            "html_url": info.get("html_url", ""),
            "date": now,
        })
        print(f"  Unfork detected: {owner}")

    # Append new unstars (users who un-starred Truxify)
    for username in sorted(new_unstars):
        info = prev_star_map.get(username, {})
        unstars_history.append({
            "username": username,
            "avatar_url": info.get("avatar_url", ""),
            "html_url": info.get("html_url", f"https://github.com/{username}"),
            "date": now,
        })
        print(f"  Unstar detected: {username}")

    # Save all data files
    save_json("followers.json", current_followers)
    save_json("following.json", current_following)
    save_json("forks.json", current_forks)
    save_json("stars.json", current_stars)
    save_json("starred_repos.json", current_starred_repos)
    save_json("unfollowers.json", unfollowers_history)
    save_json("unfollowed.json", unfollowed_history)
    save_json("unforks.json", unforks_history)
    save_json("unstars.json", unstars_history)

    elapsed = round(time.monotonic() - start_time, 2)

    # Save snapshot
    snapshot = {
        "last_updated": now,
        "run_duration_seconds": elapsed,
        "followers_count": len(current_followers),
        "following_count": len(current_following),
        "forks_count": len(current_forks),
        "stars_count": stars_total,
        "starred_repos_count": len(current_starred_repos),
        "followers": sorted(curr_follower_names),
        "following": sorted(curr_following_names),
        "forks": sorted(curr_fork_owners),
        "stars": sorted(curr_star_users),  # usernames who starred Truxify
    }
    save_json("snapshot.json", snapshot)

    print(f"\nDone in {elapsed}s! Updated at {now}")
    print(f"  Followers: {len(current_followers)} | Following: {len(current_following)}")
    print(f"  Forks: {len(current_forks)} | Stars: {len(current_stars)}")
    print(f"  Total unfollowers: {len(unfollowers_history)} | Total unstars: {len(unstars_history)} | Total unforks: {len(unforks_history)}")


if __name__ == "__main__":
    main()
