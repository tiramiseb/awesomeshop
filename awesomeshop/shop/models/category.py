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
    def output_description(self):
        desc = self.description.get(get_locale(), u'')
        if desc:
            parts = docutils.core.publish_parts(source=desc,writer_name='html')
            return parts['body']
        elif self.parent:
            return self.parent.output_description
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

    def __unicode__(self):
        if self.parent:
            return u'{} » {}'.format(self.parent.short_name,
                                          self.short_name)
        else:
            return unicode(self.short_name)

    @classmethod
    def hierarchy(cls, parent=None):
        hierarchy = []
        for o in cls.objects(parent=parent):
            hierarchy.append((o, cls.hierarchy(o.id)))
        return hierarchy
