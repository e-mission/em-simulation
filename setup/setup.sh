#!/bin/bash

conda env create --name emsim --file setup/environment.yml

conda activate emsim

# I can't get this to work in the environment file
# maybe need to upgrade conda?
pip install git+git://github.com/riccardoscalco/Pykov@master
