#!/bin/bash

git remote remove github
git remote add github https://Krasnopolskiy:$GITHUB_ACCESS_TOKEN@github.com/Krasnopolskiy/WebinarStreamkit.git
git push github HEAD:master

exit 0
