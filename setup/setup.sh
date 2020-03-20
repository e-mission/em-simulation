#!/bin/bash

conda env create --name emsim --file setup/environment.yml

if [ -z ${CI} ] && [[ ${CI} == "true" ]] ; then
    conda activate emsim
else
    source activate emsim
fi

# I can't get this to work in the environment file
# maybe need to upgrade conda?
pip install git+git://github.com/riccardoscalco/Pykov@master
