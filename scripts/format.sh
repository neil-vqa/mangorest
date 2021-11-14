#! /usr/bin/sh

autoflake --in-place --recursive mangorest && isort mangorest && black mangorest