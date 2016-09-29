#!/bin/sh

find . -name "*.haml" | while read fname
do
    if [ "`basename $fname | cut -c 1`" != "_" ]
    then
        haml $fname > `echo $fname | sed 's/.haml$/.html/'`
    fi
done
