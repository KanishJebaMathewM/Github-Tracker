<div align="center">

<img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="60" alt="GitHub Logo" />

# GitHub Tracker

**A self-hosted, auto-updating dashboard that tracks your GitHub followers, forks, stars, and detects unfollows — powered entirely by GitHub Actions and GitHub Pages.**

[![GitHub Actions](https://img.shields.io/badge/Powered%20by-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![GitHub Pages](https://img.shields.io/badge/Hosted%20on-GitHub%20Pages-222222?logo=github&logoColor=white)](https://pages.github.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**[🔴 Live Demo](https://kanishjebamathewm.github.io/Github-Tracker/)**

</div>

---

## Overview

GitHub Tracker automatically fetches your GitHub stats every 15 minutes using GitHub Actions, stores the data as JSON files, and serves a dark-themed dashboard via GitHub Pages — no external services, no databases, no hosting costs.

Everything runs inside your own repository.

---

## Features

| Feature | Description |
|---|---|
| 👥 **Followers & Following** | Full list with avatars and profile links |
| 🚫 **Don't Follow Back** | People you follow who haven't followed back |
| 💔 **Unfollower Detection** | Tracks who unfollowed you and when |
| 🍴 **Fork Tracking** | See every fork of your repository |
| ❌ **Unfork Detection** | Detect when someone removes their fork |
| ⭐ **Star Tracking** | See stargazers with timestamps |
| 💫 **Unstar Detection** | Detect when someone removes their star |
| 🔄 **Auto-refresh** | Runs every 15 minutes via GitHub Actions schedule |
| 🔍 **Search & Filter** | Instant search across all user lists |
| 📱 **Responsive** | Works on desktop, tablet, and mobile |

---

## How It Works

```
┌─────────────────────────────────────────────────────┐
│              GitHub Actions (every 15 min)           │
│                                                      │
│  scripts/track.py                                    │
│    ├── Fetch followers, following via GitHub API     │
│    ├── Fetch forks and stargazers for TRACK_REPO     │
│    ├── Compare against previous snapshot.json        │
│    ├── Detect new unfollowers / unforks / unstars    │
│    └── Write updated JSON files to data/             │
│                                                      │
│  git commit + push  →  data/ files updated in repo   │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                 GitHub Pages                         │
│                                                      │
│  index.html  →  fetches data/*.json at page load     │
│               →  renders live dashboard in browser   │
└─────────────────────────────────────────────────────┘
```

---

## Project Structure

```
Github-Tracker/
├── .github/
│   └── workflows/
│       └── track.yml          # Actions workflow (schedule + manual trigger)
├── data/
│   ├── snapshot.json          # Latest state snapshot + counts
│   ├── followers.json         # Current followers with avatars
│   ├── following.json         # Current following with avatars
│   ├── forks.json             # Current forks with timestamps
│   ├── stars.json             # Current stargazers with timestamps
│   ├── unfollowers.json       # Historical unfollower log
│   ├── unfollowed.json        # People you stopped following
│   ├── unforks.json           # Historical unfork log
│   └── unstars.json           # Historical unstar log
├── scripts/
│   └── track.py               # Python tracking script
├── index.html                 # Dashboard frontend
└── README.md
```

---

## Setup

### Prerequisites

- A GitHub account
- A public repository you want to track (for forks/stars)

### Step 1 — Fork or clone this repository

```bash
git clone https://github.com/KanishJebaMathewM/Github-Tracker.git
cd Github-Tracker
```

Update `GITHUB_USERNAME` and `TRACK_REPO` in `.github/workflows/track.yml` to match your own account and repository.

### Step 2 — Add a Personal Access Token (for stargazers)

The default `GITHUB_TOKEN` cannot read stargazer user details from other repositories. To enable full star tracking:

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens**
2. Click **Generate new token**
3. Set repository access to your tracked repository (e.g. `Truxify`)
4. Grant **Repository → Metadata → Read-only** permission
5. Copy the generated token

Then add it as a repository secret:

1. Go to your `Github-Tracker` repo → **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `GH_PAT` — Value: your token
4. Click **Add secret**

> **Note:** Without `GH_PAT`, the star count will still be accurate (from the repo's public metadata), but individual stargazer profiles won't be listed.

### Step 3 — Enable GitHub Pages

1. Go to your repo → **Settings → Pages**
2. Under **Source**, select `Deploy from a branch`
3. Set **Branch** to `main`, folder to `/ (root)`
4. Click **Save**

Your dashboard will be live at:
```
https://<your-username>.github.io/Github-Tracker/
```

### Step 4 — Trigger the first run

1. Go to the **Actions** tab in your repo
2. Select **Track GitHub Stats** from the left sidebar
3. Click **Run workflow → Run workflow**
4. Wait ~20 seconds for the first data sync

---

## Configuration

All configuration is done through environment variables set in `.github/workflows/track.yml`:

| Variable | Description | Default |
|---|---|---|
| `GITHUB_USERNAME` | Your GitHub username to track followers/following for | `KanishJebaMathewM` |
| `TRACK_REPO` | The `owner/repo` to track forks and stars for | `KanishJebaMathewM/Truxify` |
| `GH_PAT` | Personal Access Token for stargazer user details (optional) | — |
| `GITHUB_TOKEN` | Auto-injected by Actions for pushing data commits | Auto |

---

## Data Files

All data is stored as plain JSON and committed directly to the repository.

**`snapshot.json`** — updated every run:
```json
{
  "last_updated": "2025-01-01T12:00:00+00:00",
  "run_duration_seconds": 6.4,
  "followers_count": 27,
  "following_count": 25,
  "forks_count": 236,
  "stars_count": 45,
  "followers": ["user1", "user2"],
  "following": ["user1", "user3"],
  "forks":     ["forker1", "forker2"],
  "stars":     ["stargazer1"]
}
```

**`unfollowers.json`** — append-only history log:
```json
[
  {
    "username": "some_user",
    "avatar_url": "https://avatars.githubusercontent.com/...",
    "html_url": "https://github.com/some_user",
    "date": "2025-01-01T12:00:00+00:00"
  }
]
```

---

## Tech Stack

- **Python 3.12** — tracking script (`requests` only, no heavy dependencies)
- **GitHub Actions** — scheduled automation (cron every 15 minutes)
- **GitHub Pages** — static site hosting (free, no server needed)
- **Vanilla HTML/CSS/JS** — zero frameworks, zero build step, instant load

---

## Limitations

| Limitation | Reason |
|---|---|
| Stargazer user list requires `GH_PAT` | GitHub API restricts per-user stargazer listings to repo collaborators without elevated token |
| 15-minute minimum refresh interval | GitHub Actions minimum schedule granularity |
| Unfollow detection only works after first run | Requires a baseline snapshot to compare against |
| Historical data is append-only | Unfollower/unstar logs grow over time and are never pruned automatically |

---

## License

[MIT](LICENSE) — free to use, fork, and modify.

---

<div align="center">

Made with ❤️ by [KanishJebaMathewM](https://github.com/KanishJebaMathewM)

</div>
