#!/bin/bash

# <commit operations for all local changes>

git fetch
# git log --all --oneline --graph --decorate
git add --all
git status
git commit -am "update"
git push origin main

# <commit operations for all local changes>
