#!/bin/sh

. venv/bin/activate
pybabel extract -F babel.cfg -k lazy_gettext -o awesomeshop/translations/messages.pot .

#pybabel init -i awesomeshop/translations/messages.pot -d awesomeshop/translations -l en
#pybabel init -i awesomeshop/translations/messages.pot -d awesomeshop/translations -l fr
pybabel update -i awesomeshop/translations/messages.pot -d awesomeshop/translations
