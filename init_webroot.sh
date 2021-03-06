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
    destination=`echo $source | sed "s/^$FROM/$TO/;s/.plim$/.html/"`
    mkdir -p `dirname $destination`
    if [ -e $destination ]
    then
        # If destination exists, check if it is older than source
        sourcedate=`date -r $source +%s`
        destinationdate=`date -r $destination +%s`
        if [ "$sourcedate" -gt "$destinationdate" ]
        then
            plimc $source > $destination
            echo "  * $destination"
        else
            echo "  * $destination already done"
        fi
    else
        # If destination does not exist, compile
        plimc $source > $destination
        echo "  * $destination"
    fi
done

echo "Generating local files..."
for dir in `find $FROM/local -type d`
do
    mkdir -p `echo $dir | sed "s/^$FROM/$TO/"`
done
for source in `find $FROM/local -type f`
do
    destination=`echo $source | sed "s/^$FROM/$TO/;s/.plim$/.html/"`
    if [ -e $destination ]
    then
        # If destination exists, check if it is older than source
        sourcedate=`date -r $source +%s`
        destinationdate=`date -r $destination +%s`
        if [ "$sourcedate" -gt "$destinationdate" ]
        then
            plimc $source > $destination
            echo "  * $destination"
        else
            echo "  * $destination already done"
        fi
    else
        # If destination does not exist, compile
        plimc $source > $destination
        echo "  * $destination"
    fi
done
if [ ! -e $TO/local/local.css ]
then
    touch $TO/local/local.css
fi

if [ ! -h $TO/libs ]
then
    echo "Linking libs dir..."
    ln -s ../$FROM/libs $TO
fi

echo "Linking translation files..."
for source in `find $TRANSLATIONS/* -type d`
do
    destination=`echo $source | sed "s/^$TRANSLATIONS/$TO\/l10n/"`
    mkdir -p $destination
    for fname in common dashboard shop
    do
        if [ ! -h $destination/$fname.json ]
        then
            ln -s ../../../$source/$fname.json $destination/
        fi
    done
done

echo "Installing libs with bower..."
cd $TO
bower install
