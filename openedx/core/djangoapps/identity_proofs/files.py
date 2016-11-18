"""
Image/PDF file manipulation functions related to identity proof.
"""
from cStringIO import StringIO
from collections import namedtuple
from contextlib import closing

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.translation import ugettext as _
import piexif
from PIL import Image

from openedx.core.djangoapps.profile_images.images import (
    _set_color_mode_to_rgb, _crop_image_to_square,
    _get_corrected_exif, _create_image_file
)

from .helpers import get_identity_proof_storage
from .exceptions import FileValidationError


FileType = namedtuple('FileType', ('extensions', 'mimetypes', 'magic'))

FILE_TYPES = {
    'jpeg': FileType(
        extensions=['.jpeg', '.jpg'],
        mimetypes=['image/jpeg', 'image/pjpeg'],
        magic=['ffd8'],
    ),
    'png': FileType(
        extensions=[".png"],
        mimetypes=['image/png'],
        magic=["89504e470d0a1a0a"],
    ),
    'gif': FileType(
        extensions=[".gif"],
        mimetypes=['image/gif'],
        magic=["474946383961", "474946383761"],
    ),
    'pdf': FileType(
        extensions=[".pdf"],
        mimetypes=['application/pdf', 'x-application/pdf'],
        magic=["255044462d31"],
    ),
}


def create_identity_proof(source_file, identity_proof_name, filetype):
    side_length = 278
    side_breadth = 250
    storage = get_identity_proof_storage()

    if not filetype == 'pdf':
        original = Image.open(source_file)
        image = _set_color_mode_to_rgb(original)
        image = _crop_image_to_square(image)

        scaled = image.resize((side_breadth, side_length), Image.ANTIALIAS)
        exif = _get_corrected_exif(scaled, original)
        with closing(_create_image_file(scaled, exif)) as scaled_image_file:
            storage.save(identity_proof_name, scaled_image_file)
    else:
        with closing(_create_pdf_file(source_file)) as pdf_file:
            storage.save(identity_proof_name, pdf_file)


def remove_identity_proof(identity_proof_name):
    """
    Physically remove the identity files specified as `identity_proof_name`
    """
    storage = get_identity_proof_storage()
    storage.delete(identity_proof_name)


def validate_uploaded_file(uploaded_file):
    """
    Raises FileValidationError if the server should refuse to use this
    uploaded file as the source image for a user's profile image.  Otherwise,
    returns nothing.
    """
    if uploaded_file.size > settings.IDENTITY_PROOF_MAX_BYTES:
        file_upload_too_large = _(
            u'The file must be smaller than {file_max_size} in size.'
        ).format(
            file_max_size=_user_friendly_size(settings.IDENTITY_PROOF_MAX_BYTES)
        )
        raise FileValidationError(file_upload_too_large)
    elif uploaded_file.size < settings.IDENTITY_PROOF_MIN_BYTES:
        file_upload_too_small = _(
            u'The file must be at least {file_min_size} in size.'
        ).format(
            file_min_size=_user_friendly_size(settings.IDENTITY_PROOF_MIN_BYTES)
        )
        raise FileValidationError(file_upload_too_small)

    # check the file extension looks acceptable
    filename = unicode(uploaded_file.name).lower()
    filetype = [ft for ft in FILE_TYPES if any(filename.endswith(ext) for ext in FILE_TYPES[ft].extensions)]
    if not filetype:
        file_upload_bad_type = _(
            u'The file must be one of the following types: {valid_file_types}.'
        ).format(valid_file_types=_get_valid_file_types())
        raise FileValidationError(file_upload_bad_type)
    filetype = filetype[0]

    # check mimetype matches expected file type
    if uploaded_file.content_type not in FILE_TYPES[filetype].mimetypes:
        file_upload_bad_mimetype = _(
            u'The Content-Type header for this file does not match '
            u'the file data. The file may be corrupted.'
        )
        raise FileValidationError(file_upload_bad_mimetype)

    # check magic number matches expected file type
    headers = FILE_TYPES[filetype].magic
    if uploaded_file.read(len(headers[0]) / 2).encode('hex') not in headers:
        file_upload_bad_ext = _(
            u'The file name extension for this file does not match '
            u'the file data. The file may be corrupted.'
        )
        raise FileValidationError(file_upload_bad_ext)
    # avoid unexpected errors from subsequent modules expecting the fp to be at 0
    uploaded_file.seek(0)

    try:
        extension = filename.split(".")[1]
    except:
        extension = filetype

    return extension


def _create_pdf_file(pdf):
    string_io = StringIO()
    string_io.write(pdf.read())
    pdf_file = ContentFile(string_io.getvalue())
    return pdf_file


def _get_valid_file_types():
    """
    Return comma separated string of valid file types.
    """
    return ', '.join([', '.join(FILE_TYPES[ft].extensions) for ft in FILE_TYPES.keys()])


def _user_friendly_size(size):
    """
    Convert size in bytes to user friendly size.

    Arguments:
        size (int): size in bytes

    Returns:
        user friendly size
    """
    units = [_('bytes'), _('KB'), _('MB')]
    i = 0
    while size >= 1024 and i < len(units):
        size /= 1024
        i += 1
    return u'{} {}'.format(size, units[i])
