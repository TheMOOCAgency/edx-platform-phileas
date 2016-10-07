"""
This module implements the upload and remove endpoints of the identity proof api.
"""
from contextlib import closing
import datetime
import itertools
import logging

from django.utils.translation import ugettext as _
from django.utils.timezone import utc
from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from openedx.core.djangoapps.user_api.errors import UserNotFound
from openedx.core.lib.api.authentication import (
    OAuth2AuthenticationAllowInactiveUser,
    SessionAuthenticationAllowInactiveUser,
)
from openedx.core.lib.api.parsers import TypedFileUploadParser
from openedx.core.lib.api.permissions import IsUserInUrl
from openedx.core.lib.api.view_utils import DeveloperErrorViewMixin
from .helpers import set_has_identity_proof
from .exceptions import FileValidationError
from .files import (
    FILE_TYPES, validate_uploaded_file, create_identity_proof, remove_identity_proof
)

log = logging.getLogger(__name__)

LOG_MESSAGE_CREATE = 'Generated and uploaded identity file %(file_name)s for user %(user_id)s'
LOG_MESSAGE_DELETE = 'Deleted identity file %(file_name)s for user %(user_id)s'


def _make_upload_dt():
    """
    Generate a server-side timestamp for the upload. This is in a separate
    function so its behavior can be overridden in tests.
    """
    return datetime.datetime.utcnow().replace(tzinfo=utc)


class IdentityProofView(DeveloperErrorViewMixin, APIView):

    parser_classes = (MultiPartParser, FormParser, TypedFileUploadParser)
    authentication_classes = (OAuth2AuthenticationAllowInactiveUser, SessionAuthenticationAllowInactiveUser)
    permission_classes = (permissions.IsAuthenticated, IsUserInUrl)

    upload_media_types = set(itertools.chain(*(image_type.mimetypes for image_type in FILE_TYPES.values())))

    def post(self, request, username):
        # validate request:
        # verify that the user's
        # ensure any file was sent
        if 'file' not in request.FILES:
            return Response(
                {
                    "developer_message": u"No file provided for profile image",
                    "user_message": _(u"No file provided for profile image"),

                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # process the upload.
        uploaded_file = request.FILES['file']

        # no matter what happens, delete the temporary file when we're done
        with closing(uploaded_file):

            # file validation.
            try:
                filetype = validate_uploaded_file(uploaded_file)
            except FileValidationError as error:
                return Response(
                    {"developer_message": error.message, "user_message": error.user_message},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # remove previous uploads if any
            try:
                self.delete(request, username)
            except:
                pass

            # generate identity proof and store them
            identity_proof_name = request.user.email + "." + filetype
            create_identity_proof(uploaded_file, identity_proof_name, filetype)

            # update the user account to reflect that a identity proof is available.
            set_has_identity_proof(username, True, _make_upload_dt(), filetype)

            log.info(
                LOG_MESSAGE_CREATE,
                {'file_name': identity_proof_name, 'user_id': request.user.id}
            )

        # send client response.
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, username):

        try:
            # update the user account to reflect that the images were removed.
            set_has_identity_proof(username, False)

            # remove physical files from storage.
            extension = request.user.profile.identity_proof_file_extension
            identity_proof_name = request.user.email + "." + str(extension)
            remove_identity_proof(identity_proof_name)

            log.info(
                LOG_MESSAGE_DELETE,
                {'file_name': identity_proof_name, 'user_id': request.user.id}
            )
        except UserNotFound:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # send client response.
        return Response(status=status.HTTP_204_NO_CONTENT)


class IdentityProofUploadView(APIView):

    parser_classes = IdentityProofView.parser_classes
    authentication_classes = IdentityProofView.authentication_classes
    permission_classes = IdentityProofView.permission_classes

    def post(self, request, username):
        return IdentityProofView().post(request, username)


class IdentityProofRemoveView(APIView):

    authentication_classes = IdentityProofView.authentication_classes
    permission_classes = IdentityProofView.permission_classes

    def post(self, request, username):
        return IdentityProofView().delete(request, username)
