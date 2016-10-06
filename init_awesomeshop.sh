#!/bin/sh
# Copyright 2015-2016 Sébastien Maccagnoni
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

read -p "This file will install requirements and initialize AwesomeShop.
It is tailored for Ubuntu and Debian.

Are you sure you want to continue? [y/N] " confirm

confirm=`echo "$confirm" | tr '[A-Z]' '[a-z]'`

if [ "$confirm" != "y" -a "$confirm" != "yes" ]
then
    echo "Cancelling the initialization"
    exit 1
fi

sudo apt-get install python-virtualenv gcc python-dev libjpeg-dev libpng-dev libssl-dev
virtualenv --system-site-packages venv
. venv/bin/activate
pip install -r requirements.txt
