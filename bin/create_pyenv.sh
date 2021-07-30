#!/bin/bash

cd $(dirname $0)/../
virtualenv -p python3 pyenv

pip install -r requirements.txt