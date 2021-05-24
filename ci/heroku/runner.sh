#!/bin/bash

git remote add heroku https://heroku:$HEROKU_API_KEY@git.heroku.com/webinar-streamkit.git
git push -v heroku master
exit 0
