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

from flask import redirect, request, url_for

from ... import app
from ...helpers import admin_required, render_template
from ...shop.models import Tax
from ..forms import TaxForm

@app.route('/dashboard/taxes/', methods=['GET', 'POST'])
@app.route('/dashboard/taxes', methods=['GET', 'POST'])
@admin_required
def dashboard_taxes():
    allforms = []
    # All existing rates
    for tax in Tax.objects:
        thisform = TaxForm(request.form, tax, prefix=str(tax.id))
        if thisform.validate_on_submit():
            thisform.populate_obj(tax)
            rate.save()
            return redirect(url_for('dashboard_taxes'))
        allforms.append(thisform)
    # New form for a new rate
    newform = TaxForm(request.form, prefix="new")
    if newform.validate_on_submit():
        newtax = Tax()
        newform.populate_obj(newtax)
        newtax.save()
        return redirect(url_for('dashboard_taxes'))
    # Rendering
    return render_template('dashboard/taxes.html',
                           allforms=allforms,
                           newform=newform)

@app.route('/dashboard/taxes/remove-<tax_id>')
@admin_required
def dashboard_remove_tax(tax_id):
    Tax.objects(id=tax_id).delete()
    return redirect(url_for('dashboard_taxes'))
