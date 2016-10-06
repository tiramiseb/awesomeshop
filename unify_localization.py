#!/usr/bin/env python2

LANGUAGES = ['en', 'fr']

import json

# First, read all locales
locales = {}
for l in LANGUAGES:
    try:
        with file('locale-{}.json'.format(l), 'r') as translations:
            locales[l] = json.load(translations)
    except IOError, e:
        # No such file
        if e.errno == 2:
            locales[l] = {}
        else:
            raise

# Then, make sure all translations are in all languages
for strings in locales.values():
    for refstring in strings:
        for otherstrings in locales.values():
            if refstring not in otherstrings:
                otherstrings[refstring] = u''

# Finally, save files
for l, strings in locales.iteritems():
    with file('locale-{}.json'.format(l), 'w') as translations:
        json.dump(strings, translations, indent=0, sort_keys=True)
