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

import os.path

from whoosh import qparser
from whoosh.index import open_dir

from . import app
from .page.models import Page
from .shop.models import Category, BaseProduct

doc_index = open_dir(app.config['SEARCH_INDEX_PATH'], indexname='doc')
category_index = open_dir(app.config['SEARCH_INDEX_PATH'],indexname='category')
product_index = open_dir(app.config['SEARCH_INDEX_PATH'], indexname='product')

doc_parser = qparser.MultifieldParser(['title', 'text'],
                                      schema=doc_index.schema)
category_parser = qparser.QueryParser('name', schema=category_index.schema)
product_parser = qparser.MultifieldParser(['name', 'description',
                                           'reference', 'keywords'],
                                          schema=product_index.schema)

def search(terms):
    with doc_index.searcher() as searcher:
        docs = []
        for hit in searcher.search(doc_parser.parse(terms), collapse='doc', limit=None):
            try:
                doc = Page.objects.get(id=hit['doc'], pagetype='doc')
                docs.append(doc)
            except Page.DoesNotExist:
                pass
    with category_index.searcher() as searcher:
        categories = []
        for hit in searcher.search(category_parser.parse(terms), collapse='doc', limit=None):
            try:
                category = Category.objects.get(id=hit['doc'])
                categories.append(category)
            except Category.DoesNotExist:
                pass
    with product_index.searcher() as searcher:
        products = []
        for hit in searcher.search(product_parser.parse(terms), collapse='doc', limit=None):
            try:
                product = BaseProduct.objects.get(id=hit['doc'])
                products.append(product)
            except BaseProduct.DoesNotExist:
                pass
    return {
            'docs_result': docs,
            'categories_result': categories,
            'products_result': products
            }
