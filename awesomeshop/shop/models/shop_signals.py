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

"""
Signals must be attached to each product type :
attaching to BaseProduct does not work
(we are talking about senders here)
"""

from mongoengine import signals

from ...helpers import slugify_slug
from .category import Category
from .product import BaseProduct, product_types
from .url import update_category_url, update_product_url, remove_url


# Update urls when creating or modifying categories
signals.post_save.connect(update_category_url, sender=Category)
signals.pre_delete.connect(remove_url, sender=Category)
# Update categories slugs
signals.pre_save.connect(slugify_slug, sender=Category)


for prod_name, prod_obj in product_types:
    # Delete photo files when deleting a product
    signals.pre_delete.connect(BaseProduct.remove_photos_from_disk,
                               sender=prod_obj)
    # Update urls when creating or modifying products
    signals.post_save.connect(update_product_url, sender=prod_obj)
    signals.pre_delete.connect(remove_url, sender=prod_obj)
    # Update slugs
    signals.pre_save.connect(slugify_slug, sender=prod_obj)
