import base64
import datetime
import uuid
from os import urandom

from flask import request
from flask.ext.babel import lazy_gettext
from flask.ext.login import current_user, UserMixin
from geoip import geolite2
from scrypt import hash as scrypt_hash

from .. import db, get_locale
from ..mail import send_message
from ..shipping.models import Country, CountriesGroup, Carrier

class User(db.Document, UserMixin):
    created_at = db.DateTimeField(db_field='create',
                                  default=datetime.datetime.now, required=True)
    email = db.EmailField(unique=True,
                          verbose_name=lazy_gettext('Email address'))
    passsalt = db.StringField(db_field='salt')
    passhash = db.StringField(db_field='hash')
    is_admin = db.BooleanField(
                    db_field='adm',
                    default=False,
                    verbose_name=lazy_gettext('Is an administrator')
                    )
    locale = db.StringField()
    confirm_code = db.StringField(db_field='confirm')

    meta = {
        'ordering': ['email']
    }

    def __unicode__(self):
        return self.email

    @classmethod
    def register(cls, email, password):
        user = cls(email=email)
        user.set_password(password)
        user.send_confirmation_email()
        user.locale = get_locale(from_user=False)
        return user

    def set_password(self, password):
        salt = base64.b64encode(urandom(64))
        self.passsalt = salt
        self.passhash = base64.b64encode(
                scrypt_hash(
                    password.encode('utf-8'),
                    salt.encode('utf-8')))


    def check_password(self, password):
        candidate_hash = base64.b64encode(
                scrypt_hash(
                    password.encode('utf-8'),
                    self.passsalt.encode('utf-8')))
        return self.passhash.encode('utf-8') == candidate_hash

    def set_email(self, email):
        self.email = email
        self.send_confirmation_email()

    def delete(self, *args, **kwargs):
        """Delete the addresses before deleting the user"""
        for a in self.addresses:
            a.delete()
        db.Document.delete(self, *args, **kwargs)

    @property
    def addresses(self):
        return Address.objects(user=current_user.to_dbref())

    @property
    def orders(self):
        from ..shop.models import Order
        return Order.objects(customer=current_user.to_dbref())

    def send_confirmation_email(self):
        self.confirm_code = str(uuid.uuid4())
        send_message(self.email, 'email_confirmation', code=self.confirm_code)

def geolocate_country():
    lookup = geolite2.lookup(request.remote_addr)
    if lookup:
        try: return Country.objects.get(code=lookup.country)
        except Country.DoesNotExist: pass
    return None
class Address(db.Document):
    user = db.ReferenceField('User',
                             required=True,
                             reverse_delete_rule=db.CASCADE)
    title = db.StringField(required=True,
                           max_length=50,
                           default=lazy_gettext('My address'),
                           verbose_name=lazy_gettext('Address title'))
    firstname = db.StringField(
                        db_field='fname',
                        required=True,
                        max_length=100,
                        verbose_name=lazy_gettext('First name'))
    lastname = db.StringField(
                        db_field='lname',
                        required=True,
                        max_length=100,
                        verbose_name=lazy_gettext('Last name'))
    address = db.StringField(db_field='addr',
                             required=True,
                             verbose_name=lazy_gettext('Address'))
    country = db.ReferenceField(Country, verbose_name=lazy_gettext('Country'),
                                reverse_delete_rule=db.DENY,
                                default=geolocate_country)
    phone = db.StringField(max_length=50, verbose_name=lazy_gettext('Phone'))

    meta = {
        'ordering': ['title']
    }

    def carriers(self, weight):
        carriers = []
        groups = []
        for g in CountriesGroup.objects:
            if self.country in g.countries:
                groups.append(g)
        for c in Carrier.objects:
            this_prices = []
            p = c.get_price(self.country.id, weight)
            if p:
                this_prices.append(p)
            for g in groups:
                p = c.get_price(g.id, weight)
                if p:
                    this_prices.append(p)
            p = c.get_price('rest', weight)
            if p:
                this_prices.append(p)
            if this_prices:
                this_prices.sort()
                carriers.append((c, this_prices[0]))
        
        carriers.sort(key=lambda c: c[1]['net'])
        return carriers
