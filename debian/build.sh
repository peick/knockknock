#!/bin/sh
set -e

cd `readlink -f $0`/../../..
rsync -av --exclude knockknock/.tox --exclude "*.pyc" knockknock /tmp

cd /tmp/knockknock
rm -f /tmp/knockknock*.deb
dpkg-buildpackage -uc -us

sudo dpkg -i /tmp/knockknock*.deb
