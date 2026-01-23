# Automatic PR Test Deployment Options

This document outlines solutions for automatically deploying the test app on Heroku when there are new pull requests.

## Current Setup

- **Production app**: Uses Heroku's GitHub deployment method, auto-deploys from `master` branch
- **Test app**: Uses Heroku Git deployment method (manual)
- **Source code**: Hosted on GitHub

## Option 1: Heroku Review Apps (Recommended for PRs)

This creates a **temporary app for each PR** automatically, which is ideal for testing PRs in isolation.

### Setup Steps

1. Create a Heroku Pipeline and add both your prod and test apps to it
2. Enable Review Apps in the pipeline settings
3. Add `app.json` to your repository:

```json
{
  "name": "help-ukraine-bot",
  "description": "Telegram bot for Ukrainian refugees",
  "repository": "https://github.com/YOUR_USERNAME/help-ukraine-bot",
  "env": {
    "APP_NAME": {
      "description": "App name for bot mode",
      "value": "REVIEW"
    },
    "TOKEN": {
      "description": "Telegram bot token"
    },
    "MONGO_HOST": {
      "description": "MongoDB host"
    },
    "MONGO_USER": {
      "description": "MongoDB user"
    },
    "MONGO_PASS": {
      "description": "MongoDB password"
    },
    "MONGO_BASE": {
      "description": "MongoDB database"
    }
  },
  "buildpacks": [
    {
      "url": "heroku/python"
    }
  ]
}
```

### Pros
- Isolated testing per PR
- Automatic cleanup when PR closes
- Each PR gets its own URL for testing

### Cons
- Need to manage environment variables per review app
- Requires Heroku Pipeline setup

## Option 2: GitHub Actions (Single Test App)

Deploy to your **existing test app** on every PR using GitHub Actions.

### Setup Steps

1. Create `.github/workflows/deploy-test.yml`:

```yaml
name: Deploy to Test App

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Deploy to Heroku
        env:
          HEROKU_API_KEY: ${{ secrets.HEROKU_API_KEY }}
          HEROKU_APP_NAME: your-test-app-name
        run: |
          git push https://heroku:$HEROKU_API_KEY@git.heroku.com/$HEROKU_APP_NAME.git HEAD:main --force
```

2. Add `HEROKU_API_KEY` to GitHub Repository Secrets:
   - Go to GitHub repo → Settings → Secrets and variables → Actions
   - Create new secret named `HEROKU_API_KEY`
   - Get your Heroku API key from: https://dashboard.heroku.com/account

### Pros
- Simple setup
- Uses existing test app
- No additional Heroku infrastructure needed

### Cons
- Multiple concurrent PRs would overwrite each other on the test app
- Only one PR can be tested at a time

## Option 3: Switch Test App to GitHub Integration

Change your test app to use GitHub integration like prod, but point it to a `develop` or `staging` branch.

### Setup Steps

1. Create a `develop` branch in your repository
2. In Heroku test app settings:
   - Change deployment method from "Heroku Git" to "GitHub"
   - Connect to your repository
   - Enable automatic deploys from `develop` branch

### Workflow
- PRs merge to `develop` → auto-deploys to test app
- `develop` merges to `master` → auto-deploys to prod app

### Pros
- Same deployment method as production
- Simple branch-based workflow
- No GitHub Actions or Pipeline setup needed

### Cons
- Requires PR to be merged to `develop` before testing
- Cannot test multiple PRs simultaneously
- Need to maintain an additional branch

## Recommendation

**For this project**: Option 1 (Review Apps) is recommended if you want to test multiple PRs independently. Option 2 (GitHub Actions) is simpler if you only need to test one PR at a time and want quick setup.
