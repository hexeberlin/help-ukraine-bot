# Help Ukraine Bot

![build status](https://github.com/hexeberlin/help-ukraine-bot/actions/workflows/build.yml/badge.svg)

Telegram bot containing the answers to the FAQs for Ukrainian refugees in Berlin.

Support us: https://ko-fi.com/berlinhelpsukrainians

## Local development
To run the bot locally, add this lines to your `settings.env` file and replace the token with your bot token for local 
development.

```env
[DEVELOPMENT]
APP_NAME=TESTING
TOKEN=very_secret_token
```

## Deploy

### Automatic Deployment

**Production** (`telegram-bot-help-in-berlin`):
- Automatically deploys when a PR is merged to `master` branch

**Test** (`telegram-bot-help-in-berlin-te`):
- Automatically deploys when a PR is opened or updated to `master` branch
- Only deploys if tests pass (via GitHub Actions)
- Test bot: https://t.me/+pgshscn8iYM3M2Ey
- View deployment status in the GitHub Actions tab

**Note**: Multiple concurrent PRs will overwrite each other on the test app (last one wins).

### Manual Deployment (if needed)

Production:
```shell
heroku git:remote -a telegram-bot-help-in-berlin
git push heroku master
```

Test:
```shell
heroku git:remote -a telegram-bot-help-in-berlin-te
git push heroku <branch>:main --force
```

The command `heroku git:remote -a ...` creates a [remote](https://git-scm.com/docs/git-remote) named `heroku` in your local git repository. This can be inspected using `git remote -v`.

### IMPORTANT
When used in a chat, the bot should have ADMIN rights.
