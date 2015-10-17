from flask.ext.babel import lazy_gettext
from flask.ext.wtf import Form
from wtforms.fields import BooleanField, StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired

from ..mongo import model_form
from ..auth.models import User, Address
from ..page.models import Page
from ..shipping.models import Country, CountriesGroup, Carrier
from ..shop.models import Tax, Category, Product

UserForm = model_form(User)
class UserForm(Form):
    email = StringField(lazy_gettext('Email address'),
                        validators=[InputRequired(), Email()])
    is_admin = BooleanField(lazy_gettext('Is an administrator'))
    password = PasswordField(lazy_gettext('Password'), validators=[
                            EqualTo(
                                'password_again',
                                lazy_gettext('Passwords must be identical.'))
                            ])
    password_again = PasswordField(lazy_gettext('Password (again)'))

AddressForm = model_form(Address, exclude=['user'])

CountryForm = model_form(Country)
CountriesGroupForm = model_form(CountriesGroup)

CarrierForm = model_form(Carrier, field_args={
    'weights': {
        'min_entries': 1
        }
    })

TaxForm = model_form(Tax)

CategoryForm = model_form(Category, field_args={
    'parent': {
        'allow_blank': True
        }
    })

ProductForm = model_form(Product)

PageForm = model_form(Page)

