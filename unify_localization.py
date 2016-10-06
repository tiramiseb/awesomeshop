#!/usr/bin/env python2

import codecs
import json
import os


print "Read all existing translations..."
languages = os.listdir('translations')
translations = {}
for l in languages:
    for jsonfile in os.listdir(os.path.join('translations', l)):
        if jsonfile not in translations:
            translations[jsonfile] = {}
        translations[jsonfile][l] = json.load(
                                file(os.path.join('translations', l, jsonfile))
                                )

print "Make sure all translations exist in all languages..."
for jsonfile, langs in translations.iteritems():
    print "     ... checking {}".format(jsonfile)
    for l in languages:
        if l not in langs:
            langs[l] = {}
    for strings in langs.values():
        for refstring in strings:
            for otherlang, otherstrings in langs.iteritems():
                if refstring not in otherstrings:
                    print ' ... adding "{}" to {}'.format(refstring, otherlang)
                    otherstrings[refstring] = u''

print "Save updated files..."
for jsonfile, langs in translations.iteritems():
    for lang, strings in langs.iteritems():
        with codecs.open(
                os.path.join('translations', lang, jsonfile),
                'w',
                encoding='utf-8'
                ) as targetfile:
            json.dump(strings, targetfile, indent=0, ensure_ascii=False,
                      separators=(',', ': '), sort_keys=True)
