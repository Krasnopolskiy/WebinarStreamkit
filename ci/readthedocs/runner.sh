#!/bin/bash

git remote add github https://$GITHUB_ACCESS_TOKEN@github.com/Krasnopolskiy/WebinarStreamkit.git
git push github HEAD:master
exit 0
