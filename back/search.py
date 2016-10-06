# -*- coding: utf8 -*-

# Copyright 2015-2016 Sébastien Maccagnoni
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
from whoosh.analysis import CharsetFilter, SimpleAnalyzer
from whoosh.fields import Schema, ID, KEYWORD, TEXT
from whoosh.index import create_in, exists_in, open_dir
from whoosh.query import FuzzyTerm
from whoosh.support.charset import accent_map

from . import app
from .page.api import PageSchemaForList
from .page.models import Page
from .shop.api.category import CategorySchemaForFlatList
from .shop.api.product import BaseProductSchemaForList
from .shop.models.category import Category
from .shop.models.product import BaseProduct


indexes = {}
parsers = {}
domotego_analyzer = SimpleAnalyzer() | CharsetFilter(accent_map)


class FuzzierTerm(FuzzyTerm):
    def __init__(self, fieldname, text, boost=1.0, maxdist=3,
                 prefixlength=1, constantscore=True):
        super(FuzzierTerm, self).__init__(fieldname, text, boost, maxdist,
                                          prefixlength, constantscore)


def init_indexes_and_parsers():
    path = app.config['SEARCH_INDEX_PATH']
    # Initialize the documentations index
    name = 'doc'
    if exists_in(path, indexname=name):
        indexes['doc'] = open_dir(path, indexname=name)
    else:
        try:
            os.makedirs(path)
        except OSError:
            pass
        schema = Schema(
                        id=ID(stored=True, unique=True),
                        )
        schema.add(
                'title_*',
                TEXT(field_boost=2.0, analyzer=domotego_analyzer),
                glob=True
                )
        schema.add('text_*', TEXT(analyzer=domotego_analyzer), glob=True)
        indexes['doc'] = create_in(path, schema, indexname=name)
        index_docs(Page.objects(pagetype='doc'))
    # Initialize the categories index
    name = 'category'
    if exists_in(path, indexname=name):
        indexes['category'] = open_dir(path, indexname=name)
    else:
        try:
            os.makedirs(path)
        except OSError:
            pass
        schema = Schema(
                        id=ID(stored=True, unique=True),
                        )
        schema.add(
                'name_*',
                TEXT(field_boost=2.0, analyzer=domotego_analyzer),
                glob=True
                )
        schema.add(
                'description_*',
                TEXT(analyzer=domotego_analyzer),
                glob=True
                )
        indexes['category'] = create_in(path, schema, indexname=name)
        index_categories(Category.objects)
    # Initialize the products index
    name = 'product'
    if exists_in(path, indexname=name):
        indexes['product'] = open_dir(path, indexname=name)
    else:
        try:
            os.makedirs(path)
        except OSError:
            pass
        schema = Schema(
                        id=ID(stored=True, unique=True),
                        reference=KEYWORD,
                        keywords=KEYWORD(lowercase=True, field_boost=1.5)
                        )
        schema.add(
                'name_*',
                TEXT(field_boost=2.0, analyzer=domotego_analyzer),
                glob=True
                )
        schema.add(
                'description_*',
                TEXT(analyzer=domotego_analyzer),
                glob=True
                )
        indexes['product'] = create_in(path, schema, indexname=name)
        index_products(BaseProduct.objects)

    # Initialize the parsers
    docparserfields = []
    categoryparserfields = []
    productparserfields = ['reference', 'keywords']
    for lg in app.config['LANGS']:
        docparserfields.append('title_'+lg)
        docparserfields.append('text_'+lg)
        categoryparserfields.append('name_'+lg)
        categoryparserfields.append('description_'+lg)
        productparserfields.append('name_'+lg)
        productparserfields.append('description_'+lg)
    parsers['doc'] = qparser.MultifieldParser(
                                    docparserfields,
                                    schema=indexes['doc'].schema,
                                    termclass=FuzzierTerm
                                    )
    parsers['category'] = qparser.MultifieldParser(
                                    categoryparserfields,
                                    schema=indexes['category'].schema,
                                    termclass=FuzzierTerm
                                    )
    parsers['product'] = qparser.MultifieldParser(
                                    productparserfields,
                                    schema=indexes['product'].schema,
                                    termclass=FuzzierTerm
                                    )


def index_docs(objs):
    writer = indexes['doc'].writer()
    langs = app.config['LANGS']
    for i in objs:
        obj = {
                'id': unicode(i.id)
                }
        for lg in langs:
            obj['title_'+lg] = i.title.get(lg, u'')
            obj['text_'+lg] = i.text.get(lg, u'')
        writer.update_document(**obj)
    writer.commit()


def index_doc(obj):
    index_docs((obj,))


def delete_doc(obj):
    writer = indexes['doc'].writer()
    writer.delete_by_term('id', unicode(obj.id))
    writer.commit()


def index_categories(objs):
    writer = indexes['category'].writer()
    langs = app.config['LANGS']
    for i in objs:
        obj = {
                'id': unicode(i.id)
                }
        for lg in langs:
            obj['name_'+lg] = i.name.get(lg, u'')
            obj['description_'+lg] = i.description.get(lg, u'')
        writer.update_document(**obj)
    writer.commit()


def index_category(obj):
    index_categories((obj,))


def delete_category(obj):
    writer = indexes['category'].writer()
    writer.delete_by_term('id', unicode(obj.id))
    writer.commit()


def index_products(objs):
    writer = indexes['product'].writer()
    langs = app.config['LANGS']
    for i in objs:
        obj = {
                'id': unicode(i.id),
                'reference': i.reference,
                'keywords': i.keywords
                }
        for lg in langs:
            obj['name_'+lg] = i.name.get(lg, u'')
            obj['description_'+lg] = i.description.get(lg, u'')
        writer.update_document(**obj)
    writer.commit()


def index_product(obj):
    index_products((obj,))


def delete_product(obj):
    writer = indexes['product'].writer()
    writer.delete_by_term('id', unicode(obj.id))
    writer.commit()

init_indexes_and_parsers()


def do_search(terms):
    docs = []
    categories = []
    products = []
    if terms:
        with indexes['doc'].searcher() as searcher:
            for hit in searcher.search(
                                    parsers['doc'].parse(terms),
                                    collapse='id',
                                    limit=None
                                    ):
                try:
                    docs.append(
                            PageSchemaForList().dump(
                                Page.objects.get(id=hit['id'], pagetype='doc')
                                ).data
                            )
                except Page.DoesNotExist:
                    pass
        with indexes['category'].searcher() as searcher:
            for hit in searcher.search(
                                    parsers['category'].parse(terms),
                                    collapse='id',
                                    limit=None
                                    ):
                try:
                    categories.append(
                            CategorySchemaForFlatList().dump(
                                Category.objects.get(id=hit['id'])
                                ).data
                            )
                except Category.DoesNotExist:
                    pass
        with indexes['product'].searcher() as searcher:
            for hit in searcher.search(
                                    parsers['product'].parse(terms),
                                    collapse='id',
                                    limit=None
                                    ):
                try:
                    products.append(
                        BaseProductSchemaForList().dump(
                            BaseProduct.objects.get(id=hit['id'], on_sale=True)
                            ).data
                        )
                except BaseProduct.DoesNotExist:
                    pass
    return {
        'docs': docs,
        'categories': categories,
        'products': products
        }
