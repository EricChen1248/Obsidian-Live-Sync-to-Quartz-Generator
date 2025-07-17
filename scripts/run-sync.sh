#!/bin/sh
set -x

cd / 
python3 main.py 
cd /quartz
npx quartz build
rm -rf /content/public/*
cp -r /quartz/public/. /content/public/
chmod 777 /content/public/