#! /usr/bin/sh

flake8 mangorest tests
black mangorest tests --check
isort mangorest tests --check-only