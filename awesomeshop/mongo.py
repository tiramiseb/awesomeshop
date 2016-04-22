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

import itertools
from flask_mongoengine.wtf.orm import converts, ModelConverter, \
                                      model_form as orig_model_form
from mongoengine.fields import DictField, StringField
from wtforms import fields as f
from wtforms.utils import unset_value

from . import app


class TranslationsList(f.Field):
    """Inspired by FieldList"""

    def __init__(self, unbound_field, label=None, validators=None,
                 default=tuple(), **kwargs):
        super(TranslationsList, self).__init__(label, validators,
                                               default=default, **kwargs)
        self.unbound_field = unbound_field
        self._prefix = kwargs.get('_prefix', u'')

    def process(self, formdata, data=unset_value):
        self.entries = {}
        self.object_data = data

        if formdata:
            prefix = self.short_name+'_'
            for id_, value in formdata.items():
                if id_.startswith(prefix):
                    self._add_entry(formdata, (id_.split('_', 1)[1], value))
        else:
            for obj_data in data.items():
                self._add_entry(formdata, obj_data)
        # Finally, if a translation does not exist, add it in the form
        for lang in app.config['LANGS']:
            if lang not in self.entries:
                self._add_entry(formdata, (lang, None))

    def validate(self, form, extra_validators=tuple()):
        """Exactly the same as in FieldList, untested"""
        self.errors = []
        for subfield in self.entries.values():
            if not subfield.validate(form):
                self.errors.append(subfield.errors)

        chain = itertools.chain(self.validators, extra_validators)
        self._run_validation_chain(form, chain)

        return len(self.errors) == 0

    def populate_obj(self, obj, name):
        values = getattr(obj, name, None)
        for lang, content in self.entries.items():
            getattr(obj, name)[lang] = content.data

    def _add_entry(self, formdata=None, data=unset_value):
        lang = data[0]
        name = '{}_{}'.format(self.short_name, lang)
        id = '{}-{}'.format(self.id, lang)
        field = self.unbound_field.bind(
                    form=None,
                    name=name,
                    prefix=self._prefix,
                    id=id,
                    _meta=self.meta
                    )
        field.process(formdata, data[1])
        self.entries[lang] = field
        return field


class TranslationsField(DictField):
    """Inspired by MapField

    Use it to define translations for a string in AwesomeShop

    (database field)"""
    def __init__(self, max_length=None, **kwargs):
        super(TranslationsField, self).__init__(
                    field=StringField(max_length=max_length),
                    **kwargs
                    )


class AwesomeShopConverter(ModelConverter):
    @converts('TranslationsField')
    def conv_Translations(self, model, field, kwargs):
        """Inspired by conv_List"""
        field_args = kwargs.pop("field_args", {})
        if field.field.max_length:
            unbound_field = f.StringField(**field_args)
        else:
            unbound_field = f.TextAreaField(**field_args)
        return TranslationsList(unbound_field, **kwargs)

    # Exactly the same as the original one, but if it is defined there,
    # the correct model_form will be used, with conv_Translations
    @converts('EmbeddedDocumentField')
    def conv_EmbeddedDocument(self, model, field, kwargs):
        kwargs = {
            'validators': [],
            'filters': [],
            'default': field.default or field.document_type_obj,
        }
        form_class = model_form(field.document_type_obj, field_args={})
        return f.FormField(form_class, **kwargs)


def model_form(model, **kwargs):
    return orig_model_form(model, converter=AwesomeShopConverter(), **kwargs)
