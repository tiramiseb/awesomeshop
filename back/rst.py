# -*- coding: utf8 -*-

# Copyright 2016 Sébastien Maccagnoni
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

import re

from docutils.core import publish_parts
from docutils.nodes import bullet_list, list_item, paragraph, reference
from docutils.parsers.rst import Directive, directives

from . import get_locale


class DocList(Directive):

    def run(self):
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


def get_html(source, initial_level):
    source = re.sub('\[[^\]]*\]', internal_page_link, source)
    parts = publish_parts(
                source=source,
                settings_overrides={
                    'initial_header_level': initial_level
                    },
                writer_name='html')
    return parts['body']


def internal_page_link(match):
    """Transform "[pageslug]" to a link to the page, with the correct title."""
    from .page.models import Page
    pageslug = match.group(0)[1:-1]
    if '|' in pageslug:
        title, pageslug = pageslug.split('|')
    else:
        title = False
    try:
        page = Page.objects.get(slug=pageslug)
    except (Page.DoesNotExist, Page.MultipleObjectsReturned):
        # If a page with this slug does not exist or if there are multiple
        # pages (unlikely), return the same string
        return u'['+pageslug+u']'
    if not title:
        title = page.title.get(get_locale(), u'')
    return u'`{title} <{pagetype}/{slug}>`_'.format(
                title=title,
                pagetype=page.pagetype,
                slug=page.slug
            )
