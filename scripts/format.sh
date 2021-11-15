#! /usr/bin/sh

autoflake --imports=pymongo,bson --in-place --recursive mangorest && isort mangorest && black mangorest