#!/bin/sh

find -name "*.pyc" | xargs rm -rf

coverage erase

for f in *.test.py
do 
    coverage run --append $f --quiet
done

coverage report -m
