from flask import request, redirect, url_for

from ... import app
from ...helpers import admin_required, render_template
from ...shipping.models import Carrier
from ..forms import CarrierForm

@app.route('/dashboard/carriers')
@admin_required
def dashboard_carriers():
    return render_template('dashboard/carriers.html',
                           carriers=Carrier.objects)


@app.route('/dashboard/carrier', methods=['GET', 'POST'])
@app.route('/dashboard/carrier-<carrier_id>', methods=['GET', 'POST'])
@admin_required
def dashboard_carrier(carrier_id=None):
    if carrier_id:
        c = Carrier.objects.get_or_404(id=carrier_id)
    else:
        c = Carrier()
    form = CarrierForm(request.form, c)
    if form.validate_on_submit():
        form.populate_obj(c)
        c.save()
        return redirect(url_for('dashboard_carrier', carrier_id=c.id))
    return render_template('dashboard/carrier.html', form=form, carrier=c)

@app.route('/dashboard/carrier-<carrier_id>/set_costs', methods=['POST'])
@admin_required
def dashboard_carrier_costs(carrier_id):
    c = Carrier.objects.get_or_404(id=carrier_id)
    for entry, cost in request.form.items():
        try:
            c_or_g, w = entry.split('+')
            w = str(int(w))
            if cost:
                cost = float(cost.replace(',', '.'))
            else:
                cost = None
        except:
            # If the field is not in the form C+W
            #    or if W is not an integer
            #    or if the value is not a float
            # pass to the next one
            continue
        if c_or_g in c.costs:
            if cost: c.costs[c_or_g][w] = cost
            else: c.costs[c_or_g].pop(w, None)
        elif cost:
            c.costs[c_or_g] = {w: cost}
    c.save()
    return redirect(url_for('dashboard_carrier', carrier_id=carrier_id)+'#price')


@app.route('/dashboard/carrier-<carrier_id>/remove')
@admin_required
def dashboard_remove_carrier(carrier_id):
    Carrier.objects(id=carrier_id).delete()
    return redirect(url_for('dashboard_carriers'))
