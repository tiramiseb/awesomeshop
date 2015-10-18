import os.path, uuid
from PIL import Image

from flask.ext.babel import lazy_gettext

from . import app, db


thumb_size = app.config['THUMBNAIL_SIZE']
preview_size = app.config['PREVIEW_SIZE']
class Photo(db.EmbeddedDocument):
    filename = db.StringField(db_field='fname', max_length=50,
                              verbose_name=lazy_gettext('Filename'))

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
        if os.path.exists(n): os.remove(n)
        p = os.path.join(app.static_folder, 'photos', 'preview.'+self.filename)
        if os.path.exists(p): os.remove(p)
        t = os.path.join(app.static_folder, 'photos', 'thumb.'+self.filename)
        if os.path.exists(t): os.remove(t)

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
