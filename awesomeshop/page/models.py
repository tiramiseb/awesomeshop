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
from mongoengine.connection import get_db

from .. import db, get_locale
from ..mongo import TranslationsField
from ..photo import Photo

counters = get_db()['mongoengine.counters']


class Page(db.Document):
    pagetype = db.StringField(db_field='type')
    rank = db.SequenceField()
    slug = db.StringField(unique_with='pagetype')
    in_menu = db.BooleanField(db_field='menu')
    title = TranslationsField()
    text = TranslationsField()
    photos = db.EmbeddedDocumentListField(Photo)

    meta = {
        'ordering': ['rank']
    }

    def move_up(self, up_to=None):
        """up_to must be the object which has been initially moved"""
        rank = self.rank + 1
        try:
            nextdoc = Page.objects.get(rank=rank)
        except Page.DoesNotExist:
            # There is no next doc
            # * either because the end of the list is reached
            last_count = counters.find_one({'_id': 'page.rank'})['next']
            if rank > last_count:
                counters.find_one_and_update({'_id': 'page.rank'},
                                             {'$set': {'next': rank}})
            # * or because there is a hole in the list (perfect,
            #                                           no change elsewere)
        else:
            if nextdoc != up_to:
                nextdoc.move_up(up_to)
        self.rank = rank
        self.save()

    def move_before(self, target):
        rank = target.rank
        target.move_up(up_to=self)
        self.rank = rank
        self.save()

    def move_to_end(self):
        rank = counters.find_one({'_id': 'page.rank'})['next'] + 1
        counters.find_one_and_update({'_id': 'page.rank'},
                                     {'$set': {'next': rank}})
        self.rank = rank
        self.save()

    @property
    def content(self):
        """Return the formatted content of the page"""
        parts = docutils.core.publish_parts(
                    source=self.text.get(get_locale(), u''),
                    settings_overrides={
                        'initial_header_level': 2
                        },
                    writer_name='html')
        return parts['body']

    @property
    def products(self):
        """Return a list of products using this documentation"""
        from ..shop.models import Product
        return Product.objects(documentation=self)
