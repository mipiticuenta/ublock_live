#!/bin/bash

# <commit operations for all local changes>

git remote -v
git pull
git stash list
git stash show
git add --all
git status
git prune --verbose
echo
echo "last 5 commits:"
git log -n 5 --decorate --oneline --graph

# <commit operations for all local changes>
