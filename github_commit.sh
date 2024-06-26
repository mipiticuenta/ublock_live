#!/bin/bash

# <commit operations for all local changes>

git pull --verbose
git add --all
git status -sbv --show-stash --porcelain=v2
git commit -am "update"
git push --verbose
git prune --verbose
echo "last 5 commits:"
git log -n 5 --decorate --oneline --graph

# <commit operations for all local changes>
