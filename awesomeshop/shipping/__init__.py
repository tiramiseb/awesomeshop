# -*- coding: utf8 -*-
import json
import urllib

from .models import Country, CountriesGroup

def create_countries_from_restcountries():
    """Create all countries based on the "REST Countries" service.
    
    Please donate to its author if it is useful:
    https://restcountries.eu/"""

    # Get countries from the restcountries.eu API
    api_url = 'https://restcountries.eu/rest/v1/all'
    response = urllib.urlopen(api_url)
    countries = json.loads(response.read())
    groups = {}
    for country in countries:
        code = country['alpha2Code']
        # Create the country itself
        c = Country(code=code,
                default_name=country['nativeName'])
        for lang, name in country['translations'].items():
            if name:
                c.name[lang] = name
        c.name['en'] = country['name']
        c.save()

        # Create countries groups...
        # ... by region
        reg = country['region']
        if reg:
            try:
                group = CountriesGroup.objects.get(name=reg)
            except CountriesGroup.DoesNotExist:
                group = CountriesGroup(name=reg)
            group.countries.append(c)
            group.save()
        # ... by subregion
        subreg = country['subregion']
        if subreg:
            subreg = '{} » {}'.format(reg, subreg)
            try:
                group = CountriesGroup.objects.get(name=subreg)
            except CountriesGroup.DoesNotExist:
                group = CountriesGroup(name=subreg)
            group.countries.append(c)
            group.save()

#  European union, as of 2015
european_union = [
    # 28 member stats
    'BE', 'BG', 'CZ', 'DK', 'DE', 'EE', 'IE', 'GR', 'ES', 'FR', 'HR', 'IT',
    'CY', 'LV', 'LT', 'LU', 'HU', 'MT', 'NL', 'AT', 'PL', 'PT', 'RO', 'SI',
    'SK', 'FI', 'SE', 'GB',
    # Special territories
    'AX'
    ]
def create_legal_groups():
    eu = CountriesGroup(name='European Union')
    for code in european_union:
        eu.countries.append(Country.objects.get(code=code))
    eu.save()
