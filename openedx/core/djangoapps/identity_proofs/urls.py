"""
Author: Naresh Makwana
"""

from django.conf.urls import patterns, url

from .views import IdentityProofUploadView, IdentityProofRemoveView
from django.conf import settings


urlpatterns = patterns(
    '',
    url(
        r'^v1/' + settings.USERNAME_PATTERN + '/upload/$',
        IdentityProofUploadView.as_view(),
        name="identity_proof_upload"
    ),
    url(
        r'^v1/' + settings.USERNAME_PATTERN + '/remove/$',
        IdentityProofRemoveView.as_view(),
        name="identity_proof_remove"
    ),
)
