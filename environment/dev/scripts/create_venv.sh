#!/usr/bin/env bash
#
# Usage create_venv.sh MYENV
#
# As Ubuntu guys loves patch things they shouldn't and break everything,
# python3 developers using their awful distro must to follow the
# following steps in order to use venv instead of simply executing
# 'python -m venv env'.
#
# Thanks, Canonical QA team deserves a big shiny medal.
#

function check_in_virtualenv(){
    path=`which $1`
    if [[ $path* == $venv ]]; then
        exit 0
    fi
    exit 1
}

set -e

venv="`pwd`/$1"
cachedir="$HOME/.venv_cache"
setuptools_version=5.5.1
pip_version=1.5.6


mkdir -p $cachedir

if [ ! -d $cachedir/setuptools-$setuptools_version ]; then
    wget https://pypi.python.org/packages/source/s/setuptools/setuptools-$setuptools_version.tar.gz -P $cachedir
    tar -vzxf $cachedir/setuptools-$setuptools_version.tar.gz -C $cachedir
fi

if [ ! -d $cachedir/pip-$pip_version ]; then
    wget https://pypi.python.org/packages/source/p/pip/pip-$pip_version.tar.gz -P $cachedir
    tar -vzxf $cachedir/pip-$pip_version.tar.gz -C $cachedir
fi

python3 -m venv --without-pip $venv # pip is broken on ubuntu

source $venv/bin/activate
cd $cachedir/setuptools-$setuptools_version
python setup.py install
deactivate

source $venv/bin/activate
cd $cachedir/pip-$pip_version
python setup.py install
deactivate

source $venv/bin/activate
echo "venv created on $venv"
