# Help Ukraine Bot
Telegram bot containing the answers to the FAQs for Ukrainian refugees in Berlin.
Support us: https://ko-fi.com/berlinhelpsukrainians

## Local development
To run the bot locally, add this lines to your `settings.env` file and replace the token with your bot token for local 
development.

```env
[DEVELOPMENT]
APP_NAME=TESTING
TOKEN=very_secret_token
MONGO_HOST=host
MONGO_USER=user
MONGO_PASS=very_secret_password
MONGO_BASE=base
```

## Deploy
Main branch is automatically deployed to heroku when a PR is merged.

To deploy the main branch manually:
```shell
heroku git:remote -a telegram-bot-help-in-berlin
git push heroku master
```

To deploy the test branch:
```shell
heroku git:remote -a telegram-bot-help-in-berlin-te 
git push heroku test-deploy:master --force
```

Test bot is available in this telegram group: https://t.me/+pgshscn8iYM3M2Ey

Some details of deployment per Git push: the command `heroku git:remote -a ...`
creates a [remote](https://git-scm.com/docs/git-remote) named `heroku` in your
local git repository. This remote can be inspected using `git remote -v`. When
performing `git push heroku master`, we're pushing the current local state of
the `master` branch to that `heroku` remote. Upon this push, Heroku triggers
the re-deployment of the dyno.

### IMPORTANT
When used in a chat, the bot should have ADMIN rights.
