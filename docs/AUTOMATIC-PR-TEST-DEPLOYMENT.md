# Automatic PR Test Deployment

This document describes the current automatic test deployment strategy and alternative approaches for future consideration.

## Current Implementation: GitHub Actions Deployment ✅

Pull requests to `master` are **automatically deployed** to the test Heroku app (`telegram-bot-help-in-berlin-te`) using GitHub Actions.

### How It Works

1. **PR is opened or updated** → Build workflow triggers (`.github/workflows/build.yml`)
2. **Build job runs** → Lints code and runs tests
3. **If tests pass** → Deploy job automatically deploys to test app
4. **If tests fail** → Deploy job is skipped automatically
5. **Check deployment status** → View in GitHub Actions tab

### Technical Details

The deployment is integrated into `.github/workflows/build.yml` as a separate job:

```yaml
jobs:
  build:
    # ... lint and test steps ...

  test-deploy:
    needs: build  # Only runs if build succeeds
    if: github.event_name == 'pull_request'  # Only on PRs
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Deploy to Heroku test environment
        env:
          HEROKU_API_KEY: ${{ secrets.HEROKU_API_KEY }}
          HEROKU_APP_NAME: telegram-bot-help-in-berlin-te
        run: |
          git push https://heroku:$HEROKU_API_KEY@git.heroku.com/$HEROKU_APP_NAME.git HEAD:main --force
```

### Setup Requirements

- **GitHub Secret**: `HEROKU_API_KEY` must be added to repository secrets
  - Location: GitHub repo → Settings → Secrets and variables → Actions
  - Value: Get from https://dashboard.heroku.com/account (API Key section)

### Testing

- **Test bot**: https://t.me/+pgshscn8iYM3M2Ey
- **Check deployment status**: GitHub Actions tab
- **View logs**: `heroku logs --tail --app telegram-bot-help-in-berlin-te`

### Advantages

- ✅ Simple setup - single workflow file, one GitHub secret
- ✅ Uses existing test app (`telegram-bot-help-in-berlin-te`)
- ✅ Only deploys if tests pass (prevents broken code)
- ✅ Native job dependencies - no external actions needed
- ✅ All CI/CD logic in one place

### Limitations

- ⚠️ Multiple concurrent PRs will overwrite each other (last one wins)
- ⚠️ Only one PR can be tested at a time
- ⚠️ No automatic cleanup when PR closes

---

## Alternative Approaches for Future Consideration

### Option 1: Heroku Review Apps

Create a **temporary app for each PR** automatically, ideal for testing multiple PRs in isolation.

**Setup Steps:**
1. Create a Heroku Pipeline and add both prod and test apps
2. Enable Review Apps in pipeline settings
3. Add `app.json` to repository with environment variable definitions
4. Configure secrets at pipeline level in Heroku dashboard

**Configuration Example (`app.json`):**
```json
{
  "name": "help-ukraine-bot",
  "description": "Telegram bot for Ukrainian refugees",
  "repository": "https://github.com/hexeberlin/help-ukraine-bot",
  "env": {
    "APP_NAME": {
      "description": "App name for bot mode"
    },
    "TOKEN": {
      "description": "Telegram bot token"
    }
  },
  "buildpacks": [
    {
      "url": "heroku/python"
    }
  ]
}
```

**Pros:**
- ✅ Isolated testing per PR
- ✅ Automatic cleanup when PR closes
- ✅ Each PR gets its own URL for testing
- ✅ Multiple PRs can be tested simultaneously

**Cons:**
- ⚠️ Need to manage environment variables per review app
- ⚠️ Requires Heroku Pipeline setup
- ⚠️ Additional Heroku infrastructure complexity

### Option 2: Branch-Based GitHub Integration

Change test app to use GitHub integration (like production), pointing to a `develop` or `staging` branch.

**Setup Steps:**
1. Create a `develop` branch in repository
2. In Heroku test app settings:
   - Change deployment method from "Heroku Git" to "GitHub"
   - Connect to repository
   - Enable automatic deploys from `develop` branch

**Workflow:**
- PRs merge to `develop` → auto-deploys to test app
- `develop` merges to `master` → auto-deploys to prod app

**Pros:**
- ✅ Same deployment method as production
- ✅ Simple branch-based workflow
- ✅ No GitHub Actions or additional setup needed

**Cons:**
- ⚠️ Requires PR to be merged to `develop` before testing
- ⚠️ Cannot test multiple PRs simultaneously
- ⚠️ Need to maintain an additional branch

---

## Recommendation

The **current GitHub Actions approach** is simple and effective for projects with one active PR at a time.

**Consider switching to Heroku Review Apps** if:
- You need to test multiple PRs simultaneously
- You want isolated environments per PR
- You need automatic cleanup when PRs close
