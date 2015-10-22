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

import docutils.core
from flask.ext.babel import lazy_gettext
from mongoengine import signals
from slugify import slugify

from .. import db, get_locale
from ..mongo import TranslationsField
from ..photo import Photo


class Page(db.Document):
    pagetype = db.StringField(db_field='type', max_length=10)
    rank = db.SequenceField(required=True, verbose_name=lazy_gettext('Rank'))
    slug = db.StringField(max_length=100, required=True,
                          verbose_name=lazy_gettext('Slug'))
    in_menu = db.BooleanField(db_field='menu', default=False,
                              verbose_name=lazy_gettext('Display in menu'))
    title = TranslationsField(max_length=100)
    text = TranslationsField()
    photos = db.EmbeddedDocumentListField(Photo)

    meta = {
        'ordering': ['rank']
    }

    def __unicode__(self):
        return self.title.get(get_locale(), u'')

    def move(self, direction):
        if direction == 'down':
            target = Page.objects(
                        pagetype=self.pagetype,
                        rank__gt=self.rank
                        ).first()
        elif direction == 'up':
            target = Page.objects(
                        pagetype=self.pagetype,
                        rank__lt=self.rank
                        ).first()
        if target:
            refrank = self.rank
            self.rank = target.rank
            target.rank = refrank
            self.save()
            target.save()

    @property
    def output_text(self):
        parts = docutils.core.publish_parts(
                    source=self.text.get(get_locale(), u''),
                    settings_overrides = {
                        'initial_header_level': 2
                        },
                    writer_name='html')
        return parts['body']

    @property
    def products(self):
        from ..shop.models import Product
        return Product.objects(documentation=self)

    @classmethod
    def slugify_slug(cls, sender, document, **kwargs):
        document.slug = slugify(document.slug)

    @classmethod
    def remove_photos_from_disk(cls, sender, document, **kwargs):
        for p in document.photos:
            p.delete_files()

signals.pre_save.connect(Page.slugify_slug, sender=Page)
signals.pre_delete.connect(Page.remove_photos_from_disk, sender=Page)
