#!/usr/bin/env python

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
