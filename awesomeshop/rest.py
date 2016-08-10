# -*- coding: utf8 -*-

# Copyright 2016 Sébastien Maccagnoni-Munch
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

from docutils.nodes import bullet_list, list_item, paragraph, reference
from docutils.parsers.rst import Directive, directives


class DocList(Directive):

    def run(self):
        from . import get_locale
        from .page.models import Page
        pageslist = bullet_list()
        for page in Page.objects.filter(pagetype='doc'):
            link = reference(refuri='/doc/'+page.slug)
            link += paragraph(text=page.title.get(get_locale(), u''))
            text = paragraph()
            text += link
            item = list_item()
            item += text
            pageslist += item
        return [pageslist]

directives.register_directive('doc-list', DocList)
