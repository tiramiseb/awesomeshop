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

import docutils
from flask.ext.babel import lazy_gettext

from ... import db, get_locale
from ...mongo import TranslationsField



def next_category_rank():
    # Very very unlikely collisions, because new categories are created
    # only by an administrator
    last = Category.objects.only('rank').order_by('-rank').first()
    if last: return last.rank + 1
    else: return 1


class Category(db.Document):
    rank = db.IntField(required=True, unique=True, default=next_category_rank)
    slug = db.StringField(required=True, max_length=50,
                          verbose_name=lazy_gettext('Slug'))
    parent = db.ReferenceField('self', verbose_name=lazy_gettext('Parent'),
                               reverse_delete_rule=db.DENY)
    name = TranslationsField(max_length=50)
    description = TranslationsField()

    meta = {
        'ordering': ['rank']
    }

    @property
    def short_name(self):
        return self.name.get(get_locale(), u'')

    @property
    def full_name(self):
        if self.parent:
            return u'{} » {}'.format(self.parent.full_name, self.short_name)
        else:
            return self.short_name

    @property
    def loc_description(self):
        return self.description.get(get_locale(), u'')

    def get_description(self, initial_header_level=3):
        desc = self.loc_description
        if desc:
            parts = docutils.core.publish_parts(
                            source=desc,
                            settings_overrides = {
                                'initial_header_level': initial_header_level
                                },
                            writer_name='html'
                            )
            return parts['body']
        elif self.parent:
            return self.parent.get_description()
        return u''

    @property
    def url(self):
        from .url import Url
        return Url.objects(document=self).only('url').first().url

    @property
    def nb_products(self):
        from .product import BaseProduct
        return BaseProduct.objects(category=self, on_sale=True).count()

    @property
    def onsale_products(self):
        from .product import BaseProduct
        return BaseProduct.objects(category=self, on_sale=True)

    @property
    def children(self):
        return Category.objects(parent=self)

    @property
    def onsale_products_recursive(self):
        p = list(self.onsale_products)
        for child in self.children:
            p.extend(child.onsale_products_recursive)
        p.sort(key=unicode)
        return p

    @classmethod
    def hierarchy(cls, parent=None):
        hierarchy = []
        for o in cls.objects(parent=parent):
            hierarchy.append((o, cls.hierarchy(o.id)))
        return hierarchy
