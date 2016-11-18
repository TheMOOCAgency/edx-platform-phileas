"""
Helper functions for the accounts API.
"""
from django.conf import settings
from django.core.files.storage import get_storage_class
from django.core.exceptions import ObjectDoesNotExist

from student.models import UserProfile
from openedx.core.djangoapps.user_api.errors import UserNotFound


def set_has_identity_proof(username, is_uploaded, upload_dt=None, extension=None):
    """
    System (not user-facing) API call used to store whether the user has
    uploaded a profile image, and if so, when.  Used by profile_image API.

    Arguments:
        username (django.contrib.auth.User.username): references the user who
            uploaded an image.

        is_uploaded (bool): whether or not the user has an uploaded profile
            image.

        upload_dt (datetime.datetime): If `is_uploaded` is True, this should
            contain the server-side date+time of the upload.  If `is_uploaded`
            is False, the parameter is optional and will be ignored.

    Raises:
        ValueError: is_uploaded was True, but no upload datetime was supplied.
        UserNotFound: no user with username `username` exists.
    """
    if is_uploaded and upload_dt is None:
        raise ValueError("No upload datetime was supplied.")
    elif not is_uploaded:
        upload_dt = None
    try:
        profile = UserProfile.objects.get(user__username=username)
    except ObjectDoesNotExist:
        raise UserNotFound()

    profile.identity_proof_uploaded_at = upload_dt
    if extension:
        profile.identity_proof_file_extension = extension
    profile.save()

def get_identity_proof_storage():
    config = settings.IDENTITY_PROOF_BACKEND
    storage_class = get_storage_class(config['class'])
    return storage_class(**config['options'])
