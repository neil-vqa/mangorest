#! /usr/bin/sh

autoflake --imports=pymongo,bson --in-place --recursive mangorest tests && isort mangorest tests && black mangorest tests