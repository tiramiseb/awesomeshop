# -*- coding: utf8 -*-

# Copyright 2015-2016 Sébastien Maccagnoni-Munch
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
from .page.api import PageSchemaForList
from .page.models import Page
from .shop.api.category import CategorySchemaForFlatList
from .shop.api.product import ProductSchemaForList
from .shop.models.category import Category
from .shop.models.product import Product

doc_index = open_dir(app.config['SEARCH_INDEX_PATH'], indexname='doc')
category_index = open_dir(app.config['SEARCH_INDEX_PATH'],
                          indexname='category')
product_index = open_dir(app.config['SEARCH_INDEX_PATH'], indexname='product')

doc_parser = qparser.MultifieldParser(['title', 'text'],
                                      schema=doc_index.schema)
category_parser = qparser.QueryParser('name', schema=category_index.schema)
product_parser = qparser.MultifieldParser(['name', 'description',
                                           'reference', 'keywords'],
                                          schema=product_index.schema)


def do_search(terms):
    with doc_index.searcher() as searcher:
        docs = []
        for hit in searcher.search(
                                doc_parser.parse(terms),
                                collapse='doc',
                                limit=None
                                ):
            try:
                docs.append(
                        PageSchemaForList().dump(
                            Page.objects.get(id=hit['doc'], pagetype='doc')
                            ).data
                        )
            except Page.DoesNotExist:
                pass
    with category_index.searcher() as searcher:
        categories = []
        for hit in searcher.search(
                                category_parser.parse(terms),
                                collapse='doc',
                                limit=None
                                ):
            try:
                categories.append(
                        CategorySchemaForFlatList().dump(
                            Category.objects.get(id=hit['doc'])
                            ).data
                        )
            except Category.DoesNotExist:
                pass
    with product_index.searcher() as searcher:
        products = []
        for hit in searcher.search(
                                product_parser.parse(terms),
                                collapse='doc',
                                limit=None
                                ):
            try:
                products.append(
                        ProductSchemaForList().dump(
                            Product.objects.get(id=hit['doc'], on_sale=True)
                            ).data
                        )
            except Product.DoesNotExist:
                pass
    return {
        'docs': docs,
        'categories': categories,
        'products': products
        }
