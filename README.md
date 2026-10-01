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

## Setup (Zero Configuration!)

Everything is pre-configured for your profile (`KanishJebaMathewM`) and repo (`KanishJebaMathewM/Truxify`). **No Personal Access Tokens or repository secrets are required!**

### 1. Enable GitHub Pages

1. Go to your repo → **Settings** → **Pages**
2. Set **Source** to `Deploy from a branch`
3. Set **Branch** to `main` and folder to `/ (root)`
4. Click **Save**

### 2. Run the Workflow (or wait 15 minutes)

1. Go to the **Actions** tab in your repo
2. Click on **"Track GitHub Stats"** in the left sidebar
3. Click **"Run workflow"** → **Run workflow**
4. After ~20 seconds, your initial data will be loaded!

### 3. Visit Your Live Dashboard

Your site is live at: `https://kanishjebamathewm.github.io/Github-Tracker/`

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
