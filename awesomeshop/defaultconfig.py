# -*- coding: utf8 -*-

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

# Where to store indexes for the search engine
SEARCH_INDEX_PATH = '/tmp/awesomeshop_search'

# Shipping price multiplier before adding the preparation price
# and before taxes
SHIPPING_MULTIPLIER = 1

# How much the customer should pay for the preparation of each package
# (will be integrated into the shipping price, no detail given to the customer)
PACKAGE_PREPARATION_PRICE = 0

# Average (or minimum) weight of the package itself (will be added to the
# weight of a cart before calculating the shipping cost)
PACKAGE_WEIGHT = 0

# Rounding of the resulting shipping price (always rounding up)
SHIPPING_ROUNDING = 0.1

# Taxes on shipping (in percent)
SHIPPING_TAX = 0

# Prefix for order numbers
ORDER_PREFIX = 'ORD_'
INVOICE_PREFIX = 'INV_'

# Delays for payment
CONFIRM_DELAY = 5
PAYMENT_DELAY = 14

# Parameters for SEPA bank transfers
SEPA_TRANSFER_RECIPIENT = 'Some name'
SEPA_TRANSFER_RECIPIENT_ADDRESS = """Some address
12345 Some City"""
SEPA_TRANSFER_BIC = 'XXXXXXXX111'
SEPA_TRANSFER_IBAN = 'XX11 1111 1111 1111 1111 1111 1111 1111 11'

# Parameters for PayPlug
PAYPLUG_API_KEY='sk_test_11111111111111111111111111111111'

# Parameters for sending emails
MAIL_FROM="nobody@nowhere.com"
SMTP_SERVER="localhost"

