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

from flask.ext.babel import lazy_gettext
from slugify import slugify

from . import db

class Setting(db.Document):
    name = db.StringField(required=True, unique=True, max_length=100,
                          verbose_name=lazy_gettext('Name'))
    value = db.DynamicField()

    def __str__(self):
        return 'Setting: {} = {}'.format(self.name, self.value)

def slugify_slug(sender, document, **kwargs):
    document.slug = slugify(document.slug)
