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

### Secrets Management

**Important**: The `app.json` file above is **safe to commit** to your repository. Here's why:

- **Config vars WITH `value` field** (like `APP_NAME`): Safe to commit, these are non-sensitive settings
- **Config vars WITHOUT `value` field** (like `TOKEN`, `MONGO_PASS`): These are secrets that will NOT be stored in the repository

To provide the actual secret values to Review Apps, configure them at the **Pipeline level**:

1. Go to your Heroku Pipeline → Settings
2. Click "Reveal Config Vars" under "Review Apps"
3. Add all sensitive values here (TOKEN, MONGO_HOST, MONGO_USER, MONGO_PASS, MONGO_BASE)
4. These values will be automatically applied to all Review Apps created from this pipeline

This way, secrets are stored securely in Heroku and never committed to your Git repository. Each review app inherits the pipeline's config vars automatically.

**Alternative**: If you don't set pipeline-level config vars, Heroku will prompt you to enter them manually when creating each review app (less convenient).

### Pros
- Isolated testing per PR
- Automatic cleanup when PR closes
- Each PR gets its own URL for testing

### Cons
- Need to manage environment variables per review app
- Requires Heroku Pipeline setup

## Option 2: GitHub Actions (Single Test App) ✅ IMPLEMENTED

Deploy to the **existing test app** (`telegram-bot-help-in-berlin-te`) on every PR using GitHub Actions, integrated into the build workflow.

**Status**: Fully implemented - deployment job added to `.github/workflows/build.yml`

### Features

- ✅ Waits for build/test workflow to pass before deploying
- ✅ Deploys automatically on PR open, update, or reopen
- ✅ Uses existing test Heroku app
- ✅ Simple single-workflow approach

### Setup Steps

#### 1. Workflow Integration (Already Created)

The deployment is integrated into the existing `.github/workflows/build.yml` workflow as a separate job:

```yaml
jobs:
  build:
    # ... existing lint and test steps ...

  deploy:
    needs: build  # Only runs if build succeeds
    if: github.event_name == 'pull_request'  # Only on PRs
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Deploy to Heroku
        env:
          HEROKU_API_KEY: ${{ secrets.HEROKU_API_KEY }}
          HEROKU_APP_NAME: telegram-bot-help-in-berlin-te
        run: |
          git push https://heroku:$HEROKU_API_KEY@git.heroku.com/$HEROKU_APP_NAME.git HEAD:main --force
```

**Key points**:
- The `deploy` job depends on the `build` job via `needs: build`
- Deployment only runs on pull requests, not on pushes to master
- If tests fail, deployment is automatically skipped

#### 2. Add GitHub Secret (Required)

You need to add the Heroku API key as a GitHub secret:

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secret:
   - **Name**: `HEROKU_API_KEY`
   - **Value**: Your Heroku API key
5. To get your Heroku API key:
   - Visit https://dashboard.heroku.com/account
   - Scroll to "API Key" section
   - Click "Reveal" and copy the key

**Security note**: The API key is encrypted and only accessible to GitHub Actions workflows in this repository.

### How It Works

1. **PR is opened or updated** → Build workflow triggers
2. **Build job runs** → Lints code and runs tests
3. **If tests pass** → Deploy job automatically starts and deploys to `telegram-bot-help-in-berlin-te`
4. **If tests fail** → Deploy job is skipped automatically
5. **Check deployment status** → View in GitHub Actions tab

### Verification Steps

After adding the `HEROKU_API_KEY` secret:

1. **Open a test PR** to the `master` branch
2. **Check GitHub Actions tab** - build job runs first, then deploy job
3. **Verify deployment** - deploy job should show success after build passes
4. **Test the bot** in the Telegram group: https://t.me/+pgshscn8iYM3M2Ey
5. **Check Heroku logs** (if needed): `heroku logs --tail --app telegram-bot-help-in-berlin-te`

### Pros
- ✅ Very simple setup - just add one GitHub secret
- ✅ Uses existing test app (`telegram-bot-help-in-berlin-te`)
- ✅ No additional Heroku infrastructure needed
- ✅ Only deploys if tests pass (prevents broken code)
- ✅ Single workflow file - all CI/CD in one place
- ✅ Native job dependencies - no external actions needed

### Cons
- ⚠️ Multiple concurrent PRs will overwrite each other (last one wins)
- ⚠️ Only one PR can be tested at a time
- ⚠️ No automatic cleanup when PR closes (deployment stays until next PR)

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
