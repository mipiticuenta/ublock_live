#!/bin/bash

# <set working directory>

cd ~/git_local_repository/ublock_live
echo -e "directory changed to ~/git_local_repository/ublock_live"

# </set working directory>

# <commit operations for all local changes>

echo -e "commit&sync local changes to github"
git pull --verbose
git add --all
git status -sbv --show-stash --porcelain=v2
git commit -am "update"
git push --verbose
git prune --verbose
echo -e "last 5 commits:"
git log -n 5 --decorate --oneline --graph

# </commit operations for all local changes>

# <activate python virtual environment>

source ~/venv/bin/activate
echo -e "python virtual environment activated"

# </activate python virtual environment>

# <update ublock live>

python3 compile_from_filter_sources.py

# </update ublock live>

# <deactivate python virtual environment>

deactivate
echo -e "python virtual environment deactivated"

# </deactivate python virtual environment>

# <commit operations for all local changes>

echo -e "commit&sync local changes to github"
git pull --verbose
git add --all
git status -sbv --show-stash --porcelain=v2
git commit -am "update"
git push --verbose
git prune --verbose
echo -e "last 5 commits:"
git log -n 5 --decorate --oneline --graph

# <commit operations for all local changes>
