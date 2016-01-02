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

import os
import uuid

from flask import request
from flask_restful import Resource
from marshmallow import Schema, fields
from PIL import Image

from . import app, db, rest


thumb_size = app.config['THUMBNAIL_SIZE']
preview_size = app.config['PREVIEW_SIZE']


class Photo(db.EmbeddedDocument):
    filename = db.StringField(db_field='fname')

    @property
    def url(self):
        return os.path.join(app.static_url_path, 'photos', self.filename)

    @property
    def preview_url(self):
        return os.path.join(app.static_url_path, 'photos',
                            'preview.'+self.filename)

    @property
    def thumbnail_url(self):
        return os.path.join(app.static_url_path, 'photos',
                            'thumb.'+self.filename)

    @classmethod
    def from_request(cls, photo):
        filename, file_extension = os.path.splitext(photo.filename)
        # Create the directory
        if not os.path.exists(os.path.join(app.static_folder, 'photos')):
            os.mkdir(os.path.join(app.static_folder, 'photos'))
        # Store the image
        photo_filename = str(uuid.uuid4()) + file_extension
        filepath = os.path.join(app.static_folder, 'photos', photo_filename)
        photo.save(filepath)
        # Create the thumbnail
        thumbpath = os.path.join(app.static_folder, 'photos',
                                 'thumb.'+photo_filename)
        image = Image.open(filepath)
        image.thumbnail(thumb_size)
        image.save(thumbpath, "JPEG")
        # Create the preview
        previewpath = os.path.join(app.static_folder, 'photos',
                                   'preview.'+photo_filename)
        image = Image.open(filepath)
        image.thumbnail(preview_size)
        image.save(previewpath, "JPEG")
        # Return the document
        return cls(filename=photo_filename)

    def delete_files(self):
        n = os.path.join(app.static_folder, 'photos', self.filename)
        p = os.path.join(app.static_folder, 'photos', 'preview.'+self.filename)
        t = os.path.join(app.static_folder, 'photos', 'thumb.'+self.filename)
        if os.path.exists(n): os.remove(n)
        if os.path.exists(p): os.remove(p)
        if os.path.exists(t): os.remove(t)



class PhotoSchema(Schema):
    filename = fields.String(dump_only=True)
    url = fields.String(dump_only=True)
    preview_url = fields.String(dump_only=True)
    thumbnail_url = fields.String(dump_only=True)

