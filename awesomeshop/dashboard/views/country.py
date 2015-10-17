from flask import redirect, request, url_for

from ... import app
from ...helpers import admin_required, render_template
from ...shipping.models import Country, CountriesGroup
from ..forms import CountryForm, CountriesGroupForm

@app.route('/dashboard/countries')
@admin_required
def dashboard_countries():
    return render_template('dashboard/countries.html',
                           countries=Country.objects)

@app.route('/dashboard/country', methods=['GET', 'POST'])
@app.route('/dashboard/country-<country_id>', methods=['GET', 'POST'])
@admin_required
def dashboard_country(country_id=None):
    if country_id:
        c = Country.objects.get_or_404(id=country_id)
    else:
        c = Country()
    form = CountryForm(request.form, c)
    if form.validate_on_submit():
        form.populate_obj(c)
        c.save()
        return redirect(url_for('dashboard_countries'))
    return render_template('dashboard/country.html', form=form)

@app.route('/dashboard/country-<country_id>/remove')
@admin_required
def dashboard_remove_country(country_id):
    Country.objects(id=country_id).delete()
    return redirect(url_for('dashboard_countries'))

@app.route('/dashboard/countries_groups')
@admin_required
def dashboard_countries_groups():
    return render_template('dashboard/countries_groups.html',
                           countries_groups=CountriesGroup.objects)

@app.route('/dashboard/countries_group', methods=['GET', 'POST'])
@app.route('/dashboard/countries_group-<countries_group_id>',
           methods=['GET', 'POST'])
@admin_required
def dashboard_countries_group(countries_group_id=None):
    if countries_group_id:
        c = CountriesGroup.objects.get_or_404(id=countries_group_id)
    else:
        c = CountriesGroup()
    form = CountriesGroupForm(request.form, c)
    if form.validate_on_submit():
        form.populate_obj(c)
        c.save()
        return redirect(url_for('dashboard_countries_groups'))
    return render_template('dashboard/countries_group.html', form=form)

@app.route('/dashboard/countries_group-<countries_group_id>/remove')
@admin_required
def dashboard_remove_countries_group(countries_group_id):
    CountriesGroup.objects(id=countries_group_id).delete()
    return redirect(url_for('dashboard_countries_groups'))
