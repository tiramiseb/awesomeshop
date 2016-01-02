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

from mongoengine.connection import get_db

from .. import db
from ..mongo import TranslationsField
from ..photo import Photo

counters = get_db()['mongoengine.counters']

class Page(db.Document):
    pagetype = db.StringField(db_field='type')
    rank = db.SequenceField()
    slug = db.StringField()
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
                                             {'$set':{'next': rank}})
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
                                     {'$set':{'next': rank}})
        self.rank = rank
        self.save()
