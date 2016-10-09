#!/bin/sh
# -*- coding: utf8 -*-

# Copyright 2016 Sébastien Maccagnoni
#
# This file is part of AwesomeShop.
#
# AwesomeShop is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# AwesomeShop is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with AwesomeShop. If not, see <http://www.gnu.org/licenses/>.

FROM="front"
TRANSLATIONS="translations"
TO="webroot"

echo "Generating HTML files..."
for source in `find $FROM -name "*.plim"`
do
    destination=`echo $source | sed -s "s/^$FROM/$TO/;s/.plim$/.html/"`
    mkdir -p `dirname $destination`
    plimc $source > $destination
    echo "  * $destination"
done

echo "Generating local files..."
for dir in `find $FROM/local -type d`
do
    mkdir -p `echo $dir | sed "s/^$FROM/$TO/"`
done
for source in `find $FROM/local -type f`
do
    dest=`echo $source | sed "s/^$FROM/$TO/"`
    if [ ! -e $dest ]
    then
        echo "... $dest"
        plimc $source > $dest
    fi
done
if [ ! -e $TO/local/local.css ]
then
    touch $TO/local/local.css
fi

echo "Linking libs dir..."
ln -s ../$FROM/libs $TO

echo "Linking translation files..."
for source in `find $TRANSLATIONS/* -type d`
do
    destination=`echo $source | sed -s "s/^$TRANSLATIONS/$TO\/l10n/"`
    mkdir -p $destination
    for fname in common dashboard shop
    do
        ln -s ../../../$source/$fname.json $destination/
    done
done

echo "Installing libs with bower..."
cd $TO
bower install
