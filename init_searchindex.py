#!/usr/bin/env python
# -*- coding: utf8 -*-

# Copyright 2015 Sébastien Maccagnoni-Munch
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

# Initialize the search index.
#
# Must be executed at least once before running the app.
#
# Can be executed as many times as you want : for each execution, the index is
# deleted and recreated.

import os
import shutil
import sys

from whoosh.fields import Schema, KEYWORD, ID, TEXT
from whoosh.index import create_in

try:
    import config
except:
    pass

try: path = config.SEARCH_INDEX_PATH
except: path = None
try: langs = config.LANGS
except: langs = None

if not path or not langs:
    # Cannot import defaultconfig because it would import everything from the
    # app, resulting in an OSError on the search path
    with open('awesomeshop/defaultconfig.py', 'r') as config:
        searchok = False
        langsok = False
        for line in config.readlines():
            if not path and 'SEARCH_INDEX_PATH' in line:
                path = eval(line.split('=')[1])
                searchok = True
            if not langs and 'LANGS' in line:
                langs = eval(line.split('=')[1])
                langsok = True
            if searchok and langsok:
                break




sure = raw_input('WARNING ! {} WILL BE FLUSHED ! ARE YOU SURE [yn]? '.format(
            path))
    
if sure not in ('y', 'Y', 'yes'):
    sys.exit(1)

try: shutil.rmtree(path)
except OSError: pass
os.makedirs(path)

doc_schema = Schema(doc=ID(stored=True), title=TEXT, text=TEXT)
category_schema = Schema(doc=ID(stored=True), name=TEXT)
product_schema = Schema(doc=ID(stored=True), name=TEXT, description=TEXT,
                        reference=TEXT, keywords=KEYWORD)
    
doc_index = create_in(path, doc_schema, indexname='doc')
category_index = create_in(path, category_schema, indexname='category')
product_index = create_in(path, product_schema, indexname='product')

from awesomeshop.page.models import Page
from awesomeshop.shop.models import Category, Product

doc_writer = doc_index.writer()
for p in Page.objects(pagetype='doc'):
    for lg in langs:
        doc_writer.add_document(
                doc=unicode(p.id),
                title=p.title.get(lg, u''),
                text=p.text.get(lg, u'')
                )
doc_writer.commit()

category_writer = category_index.writer()
for c in Category.objects:
    for lg in langs:
        category_writer.add_document(doc=unicode(c.id),
                                     name=c.name.get(lg, u''))
category_writer.commit()

product_writer = product_index.writer()
for p in Product.objects:
    for lg in langs:
        product_writer.add_document(
                doc=unicode(p.id),
                name=p.name.get(lg, u''),
                description=p.description.get(lg, u''),
                reference=p.reference,
                keywords=p.keywords
                )
product_writer.commit()
