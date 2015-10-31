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

from ... import db

class Url(db.Document):
    url = db.StringField(required=True, max_length=100)
    document = db.GenericReferenceField(db_field='doc')

def update_url(sender, document, url, created, **kwargs):
    if not created:
        remove_url(sender, document)
    Url(url=url, document=document).save()
def update_category_url(sender, document, **kwargs):
    if document.parent:
        url = document.parent.url + '/' + document.slug
    else:
        url = document.slug
    update_url(sender, document, url, **kwargs)
def update_product_url(sender, document, **kwargs):
    url = document.category.url + '/' + document.slug
    update_url(sender, document, url, **kwargs)
def remove_url(sender, document, **kwargs):
    Url.objects(document=document).delete()
