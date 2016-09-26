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

import re

from mongoengine import signals
from mongoengine.connection import get_db

from .. import db, get_locale, rst
from ..mongo import TranslationsField
from ..photo import Photo

class Page(db.Document):
    pagetype = db.StringField(db_field='type')
    rank = db.SequenceField()
    slug = db.StringField(unique=True)
    in_menu = db.BooleanField(db_field='menu')
    title = TranslationsField()
    text = TranslationsField()
    photos = db.EmbeddedDocumentListField(Photo)

    meta = {
        'ordering': ['slug']
    }

    def __setattr__(self, name, value):
        if name == 'slug' and self.slug != value:
            self._previous_slug = self.slug
        super(Page, self).__setattr__(name, value)

    @property
    def content(self):
        """Return the formatted content of the page"""
        return rst.get_html(self.text.get(get_locale(), u''), 2)

    @property
    def products(self):
        """Return a list of products using this documentation"""
        from ..shop.models.product import BaseProduct
        return BaseProduct.objects(documentation=self)

    @property
    def on_sale_products(self):
        from ..shop.models.product import BaseProduct
        return BaseProduct.objects(documentation=self, on_sale=True)


def update_other_pages(sender, document, **kwargs):
    previous = getattr(document, '_previous_slug', None)
    if previous:
        for page in Page.objects:
            anychanged = False
            texts = page.text
            for lang, text in texts.iteritems():
                text, changed1 = re.subn(
                                    r'\['+previous+'\]',
                                    r'['+document.slug+']',
                                    text
                                    )
                text, changed2 = re.subn(
                                    r'\[([^\|\]]+)\|'+previous+'\]',
                                    r'[\1|'+document.slug+']',
                                    text
                                    )
                changed = changed1 + changed2
                if changed:
                    texts[lang] = text
                    anychanged = True
            if anychanged:
                page.text = texts
                page.save()


def update_search(sender, document, **kwargs):
    from ..search import index_doc
    index_doc(document)


def delete_search(sender, document, **kwargs):
    from ..search import delete_doc
    delete_doc(document)

signals.post_save.connect(update_other_pages, sender=Page)
signals.post_save.connect(update_search, sender=Page)
signals.pre_delete.connect(delete_search, sender=Page)
