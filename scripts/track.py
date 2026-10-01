import os
import json
import requests
from datetime import datetime, timezone

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME") or "KanishJebaMathewM"
TRACK_REPO = os.environ.get("TRACK_REPO") or "KanishJebaMathewM/Truxify"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"


def paginate(url):
    results = []
    page = 1
    while True:
        sep = "&" if "?" in url else "?"
        resp = requests.get(f"{url}{sep}per_page=100&page={page}", headers=HEADERS)
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


def get_stargazers():
    if not TRACK_REPO:
        return []
    # Use star media type to get starred_at timestamps
    star_headers = {**HEADERS, "Accept": "application/vnd.github.star+json"}
    results = []
    page = 1
    while True:
        resp = requests.get(
            f"https://api.github.com/repos/{TRACK_REPO}/stargazers?per_page=100&page={page}",
            headers=star_headers,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        results.extend(data)
        page += 1
    return [{
        "username": s["user"]["login"],
        "avatar_url": s["user"]["avatar_url"],
        "html_url": s["user"]["html_url"],
        "starred_at": s["starred_at"],
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
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


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

    print("Fetching stargazers...")
    current_stars = get_stargazers()
    print(f"  Found {len(current_stars)} stargazers")

    # Load previous snapshot
    prev_snapshot = load_json("snapshot.json") or {
        "followers": [], "following": [], "forks": [], "stars": []
    }

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

    # Append new unstars
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
        "stars_count": len(current_stars),
        "followers": sorted(curr_follower_names),
        "following": sorted(curr_following_names),
        "forks": sorted(curr_fork_owners),
        "stars": sorted(curr_star_users),
    }
    save_json("snapshot.json", snapshot)

    print(f"\nDone in {elapsed}s! Updated at {now}")
    print(f"  Followers: {len(current_followers)} | Following: {len(current_following)}")
    print(f"  Forks: {len(current_forks)} | Stars: {len(current_stars)}")
    print(f"  Total unfollowers: {len(unfollowers_history)} | Total unstars: {len(unstars_history)} | Total unforks: {len(unforks_history)}")


if __name__ == "__main__":
    main()
