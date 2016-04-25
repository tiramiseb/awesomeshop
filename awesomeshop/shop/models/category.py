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

from mongoengine import signals

from ... import db, get_locale
from ...mongo import TranslationsField


class Category(db.Document):
    rank = db.IntField()
    slug = db.StringField()
    parent = db.ReferenceField('self', reverse_delete_rule=db.DENY)
    name = TranslationsField()
    description = TranslationsField()

    meta = {
        'ordering': ['rank']
    }

    @classmethod
    def ordered_all(self):
        catlist = []

        def add_cats(categories, level=0):
            for cat in categories:
                cat.level = level
                catlist.append(cat)
                add_cats(cat.children, level+1)
        add_cats(self.objects(parent=None))
        return catlist

    @property
    def children(self):
        return Category.objects(parent=self)

    @property
    def path(self):
        if self.parent:
            return '{}/{}'.format(self.parent.path, self.slug)
        else:
            return self.slug

    @property
    def products(self):
        from .product import Product
        return Product.objects(category=self)

    @property
    def on_sale_products(self):
        from .product import Product
        return Product.objects(category=self, on_sale=True)

    @property
    def recursive_on_sale_products(self):
        products = list(self.on_sale_products)
        for c in self.children:
            products.extend(c.recursive_on_sale_products)
        return products

    @property
    def full_name(self):
        name = self.name.get(get_locale(), u'')
        if self.parent:
            return u'{} » {}'.format(self.parent.full_name, name)
        else:
            return name


def update_search(sender, document, **kwargs):
    from ...search import index_category
    index_category(document)


def delete_search(sender, document, **kwargs):
    from ...search import delete_category
    delete_category(document)

signals.post_save.connect(update_search, sender=Category)
signals.pre_delete.connect(delete_search, sender=Category)
