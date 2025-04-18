#!/bin/bash

BLUE='\033[1;34m'
GREEN='\033[1;32m'
RED='\033[1;31m'
NC='\033[0m' # No Color

# <set working directory>

cd ~/git_local_repository/ublock_live
echo -e "\n${BLUE}directory changed to ~/git_local_repository/ublock_live${NC}"

# </set working directory>

# <commit operations for all local changes>

echo -e "\n${BLUE}sync & upload changes to github\n${NC}"
git status -sbv --show-stash --porcelain=v2
echo -e ""
git stash push -m "stash local changes"
echo -e ""
git pull --rebase --verbose
echo -e ""
git stash pop
echo -e ""
git add --all
echo -e ""
git commit -am "update"
echo -e ""
git push --verbose
echo -e ""
git prune --verbose
echo -e "\n${BLUE}last 5 commits:\n${NC}"
git log -n 5 --decorate --oneline --graph

# </commit operations for all local changes>

# <activate python virtual environment>

source ~/venv/bin/activate
echo -e "\n${BLUE}python virtual environment activated\n${NC}"

# </activate python virtual environment>

# <update ublock live>

python3 compile_from_filter_sources.py

# </update ublock live>

# <deactivate python virtual environment>

deactivate
echo -e "\n${BLUE}python virtual environment deactivated\n${NC}"

# </deactivate python virtual environment>

# <commit operations for all local changes>

echo -e "\n${BLUE}sync & upload changes to github\n${NC}"
git status -sbv --show-stash --porcelain=v2
echo -e ""
git stash push -m "stash local changes"
echo -e ""
git pull --rebase --verbose
echo -e ""
git stash pop
echo -e ""
git add --all
echo -e ""
git commit -am "update"
echo -e ""
git push --verbose
echo -e ""
git prune --verbose
echo -e "\n${BLUE}last 5 commits:\n${NC}"
git log -n 5 --decorate --oneline --graph

# <commit operations for all local changes>
