#!/bin/bash

cd docs
export PYTHONPATH=..
make html
cd ..
mv docs/build/html public/docs

exit 0
