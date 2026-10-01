# 📊 GitHub Tracker

A self-hosted GitHub Pages dashboard that tracks your followers, following, repo forks, and detects unfollows/unforks — all powered by GitHub Actions.

## Features

- **Followers & Following** — See your full list with avatars
- **Don't Follow Back** — Find out who you follow who doesn't follow you back
- **Unfollower Detection** — Know who unfollowed you, and when
- **Fork Tracking & Unforks** — See who forked your repo and detect when forks are deleted
- **Star Tracking & Unstars** — See stargazers with timestamps and detect when someone unstars
- **Auto-updating** — GitHub Actions runs automatically every 15 minutes
- **Run Execution Speed** — Live tracking execution time displayed right on your dashboard
- **Beautiful Dashboard** — Dark-themed, responsive, searchable with instant filtering

## Setup

### 1. Create a new GitHub repo

Create a new repository (e.g., `github-tracker`) and push this code to it.

### 2. Create a Personal Access Token (PAT)

1. Go to [GitHub Settings → Developer Settings → Personal Access Tokens → Fine-grained tokens](https://github.com/settings/tokens?type=beta)
2. Create a new token with these permissions:
   - **Repository access**: All repositories (or select the tracked repo)
   - **Permissions**: `Followers` (read), `Metadata` (read)
3. Copy the token

### 3. Add Repository Secrets & Variables

Go to your repo → **Settings** → **Secrets and variables** → **Actions**:

**Secrets:**
| Name | Value |
|------|-------|
| `GH_PAT` | Your Personal Access Token from step 2 |

**Variables** (under the "Variables" tab):
| Name | Value |
|------|-------|
| `GITHUB_USERNAME` | `KanishJebaMathewM` |
| `TRACK_REPO` | `KanishJebaMathewM/Truxify` |

### 4. Enable GitHub Pages

1. Go to repo → **Settings** → **Pages**
2. Set **Source** to `Deploy from a branch`
3. Set **Branch** to `main` and folder to `/ (root)`
4. Click Save

### 5. Run the Workflow

1. Go to **Actions** tab
2. Click on **"Track GitHub Stats"**
3. Click **"Run workflow"** to trigger the first run
4. After it completes, your data will be populated

### 6. Visit Your Dashboard

Your site will be live at: `https://<your-username>.github.io/<repo-name>/`

## How It Works

```
GitHub Actions (every 15 minutes)
    ↓
scripts/track.py fetches GitHub API
    ↓
Compares with previous snapshot
    ↓
Detects unfollows / unforks / unstars
    ↓
Updates JSON files in data/
    ↓
Commits changes back to repo
    ↓
GitHub Pages serves index.html
    ↓
index.html fetches data/ JSON files
```

## Project Structure

```
├── .github/
│   └── workflows/
│       └── track.yml          # GitHub Actions workflow
├── data/
│   ├── followers.json         # Current followers
│   ├── following.json         # Current following
│   ├── forks.json             # Current forks
│   ├── unfollowers.json       # Historical unfollowers
│   ├── unfollowed.json        # People you stopped following
│   ├── unforks.json           # Historical unforks
│   └── snapshot.json          # Latest state snapshot
├── scripts/
│   └── track.py               # Tracking script
├── index.html                 # Dashboard website
└── README.md
```

## License

MIT
