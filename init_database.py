#!/usr/bin/env python
#
# Flush and initialize the MongoDB database with basic data

import sys

from mongoengine.connection import get_db

from awesomeshop import db, shipping
from awesomeshop.auth.models import Address, User
from awesomeshop.page.models import Page
from awesomeshop.shipping.models import Country, CountriesGroup, Carrier
from awesomeshop.shop.models import Tax, Category, Product, Url, Order

sure = raw_input('WARNING ! THE DATABASE WILL BE EMPTIED ! ARE YOU SURE [yn]? ')
    
if sure not in ('y', 'Y', 'yes'):
    sys.exit(1)
    
print '* Deleting previous data'
Address.drop_collection()
User.drop_collection()
Carrier.drop_collection()
CountriesGroup.drop_collection()
Country.drop_collection()
Url.drop_collection()
Product.drop_collection()
Category.drop_collection()
Tax.drop_collection()
Page.drop_collection()
Order.drop_collection()
get_db().drop_collection('mongoengine.counters')

print '* Creating an administrator (admin@example.com/admin)'
admin = User(email='admin@example.com')
admin.set_password('admin')
admin.is_admin = True
admin.save()
    
print '* Creating countries'
shipping.create_countries_from_restcountries()
shipping.create_legal_groups()
