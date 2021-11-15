#!/bin/sh
if $DEV
then
    python get_repos.py
fi
python -m MFramework bot --cfg=data/secrets.ini