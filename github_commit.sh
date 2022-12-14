#!/bin/bash

# <load configuration and git init>

# cd ~/github_local_repo
# git config --global user.name "mipiticuenta"
# git config --global user.email "mi.piticuenta@gmail.com"
# git config --global http.proxy http://10.0.0.100:8080
# git config --global https.proxy https://10.0.0.100:808
# git config --global core.editor "gedit -s"
# git init

# git config -l

# <load configuration and git init>

# <clone remote github repositories to local repo>

# git clone https://github.com/mipiticuenta/R.git
# git clone https://github.com/mipiticuenta/python.git
# git clone https://github.com/mipiticuenta/ublock_live.git

# <clone remote github repositories to local repo>

# <commit operations>

git status
git add -p
git commit -m "update"
git push origin main

# <commit operations>

