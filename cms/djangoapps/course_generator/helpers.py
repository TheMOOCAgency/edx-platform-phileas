"""
Course generator helpers
"""
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User

from xmodule.course_module import CourseFields
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import DuplicateCourseError

from opaque_keys import InvalidKeyError

from util.string_utils import _has_non_ascii_characters
from util.organizations_helpers import (
    add_organization_course,
    get_organization_by_short_name,
    organizations_enabled,
)

from contentstore.views.course import create_new_course_in_store
from openedx.core.djangoapps.models.course_details import CourseDetails


def create_course(formation):
    """
    Creates course using the provided information.

    Argument: formation dictionary

    Author: Naresh Makwana
    """
    try:
        org = formation.get('publisher')
        course = 'V' + formation.get('vodeclic_id')
        display_name = formation.get('title')
        # force the start date for reruns and allow us to override start via the client
        publish_date = formation.get('publishDate')
        publish_datetime = CourseFields.start.default
        if publish_date:
            publish_datetime = datetime.strptime(publish_date, '%Y-%m-%d')
        start = publish_datetime
        run = formation.get('publishYear') + '_T2'

        # allow/disable unicode characters in course_id according to settings
        if not settings.FEATURES.get('ALLOW_UNICODE_COURSE_ID'):
            if _has_non_ascii_characters(org) or _has_non_ascii_characters(course) or _has_non_ascii_characters(run):
                return

        fields = {'start': start}
        if display_name is not None:
            fields['display_name'] = display_name

        # Set a unique wiki_slug for newly created courses. To maintain active wiki_slugs for
        # existing xml courses this cannot be changed in CourseDescriptor.
        # # TODO get rid of defining wiki slug in this org/course/run specific way and reconcile
        # w/ xmodule.course_module.CourseDescriptor.__init__
        wiki_slug = u"{0}.{1}.{2}".format(org, course, run)
        definition_data = {'wiki_slug': wiki_slug}
        fields.update(definition_data)

        _create_new_course(formation, org, course, run, fields)

    except DuplicateCourseError:
        return
    except InvalidKeyError:
        return

def _create_new_course(formation, org, number, run, fields):
    """
    Create a new course.
    Raises DuplicateCourseError if the course already exists
    """
    org_data = get_organization_by_short_name(org)
    if not org_data and organizations_enabled():
        return
    store_for_new_course = modulestore().default_modulestore.get_modulestore_type()
    try:
        user = User.objects.get(username='coursecreator')
    except User.DoesNotExist:
        user = User.objects.create(
            username='coursecreator',
            email='coursecreator@tma.com',
            first_name='coursecreator',
            last_name='coursecreator',
            is_active=True,
            is_staff=True
        )
        user.set_password('coursecreator')
        user.save()

    new_course = create_new_course_in_store(store_for_new_course, user, org, number, run, fields)

    add_organization_course(org_data, new_course.id)

    # Set description and images for the course
    additional_info = {
        'language': formation.get('language', 'fr'),
        'short_description': formation.get('description', ''),
        'course_image_asset_path': formation.get('image_logo_url', formation.get('image_logo_url2')),
        'banner_image_asset_path': formation.get('image_jacket_url'),
        'intro_video': None,
        'start_date': new_course.start
    }

    CourseDetails.update_from_json(new_course.id, additional_info, user)
