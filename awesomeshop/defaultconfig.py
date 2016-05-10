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

DEBUG = False

# A secret key for cookies encryption. Put any random string here
SECRET_KEY = 'anything'

# How to access the MongoDB database
MONGODB_SETTINGS = {'DB': 'your_shop'}

# The shop name and description, displayed for the customers
SHOP_NAME = 'Your shop'
SHOP_DESCRIPTION = {
        'en': 'Selling things...'
        }

# Languages for the shop (optimized for 2 languages)
LANGS = ['en']

# Currency for the shop
CURRENCY = u'€'

# Size of the images in lists, etc
THUMBNAIL_SIZE = [100, 100]

# Size of the images in grid, etc
PREVIEW_SIZE = [350, 350]

# Account names (for social networks) and blog URL
FACEBOOK_ACCOUNT = ''
TWITTER_ACCOUNT = ''
BLOG_URL = ''

# The max age for new products (in days)
NEW_PRODUCTS_MAX_AGE = 60

# Where to store indexes for the search engine
SEARCH_INDEX_PATH = '/tmp/awesomeshop_search'

# Average (or minimum, as you wish) weight of the package itself (will be added
# to the weight of a cart before calculating the shipping cost) (in grams)
PACKAGE_WEIGHT = 0

# Shipping price multiplier before adding the preparation price
# and before taxes
SHIPPING_MULTIPLIER = 1

# How much the customer should pay for the preparation of each package
# (will be integrated into the shipping price, no detail given to the customer)
PACKAGE_PREPARATION_PRICE = 0

# Rounding of the resulting shipping price (always rounding up)
SHIPPING_ROUNDING = 0.1

# Taxes on shipping (in percent)
SHIPPING_TAX = 0

# Prefix for order numbers
ORDER_PREFIX = 'ORD_'
INVOICE_PREFIX = 'INV_'

# Delay for on demand orders
ON_DEMAND_DELAY_MIN = 5
ON_DEMAND_DELAY_MAX = 15

# Delays for payment
CONFIRM_DELAY = 5
PAYMENT_DELAY = 14

# Footer for the order
ORDER_FOOTER = 'Your company information here - multiline accepted'

# Parameters for SEPA bank transfers
SEPA_TRANSFER_RECIPIENT = u'Some name'
SEPA_TRANSFER_BIC = u'XXXXXXXX111'
SEPA_TRANSFER_IBAN = u'XX11 1111 1111 1111 1111 1111 1111 1111 11'

# Parameters for PayPlug
PAYPLUG_API_KEY = 'sk_test_11111111111111111111111111111111'

# Parameters for sending emails
# Really send mails ?
SEND_MAILS = True
# Sender address
MAIL_FROM = "nobody@nowhere.com"
# Mail server
SMTP_SERVER = "localhost"
