#!/bin/bash

git remote add github 'https://Krasnopolskiy:$GITHUB_ACCESS_TOKEN@github.com/Krasnopolskiy/WebinarStreamkit.git'
echo 'https://Krasnopolskiy:$GITHUB_ACCESS_TOKEN@github.com/Krasnopolskiy/WebinarStreamkit.git'
git push github HEAD:master
exit 0
