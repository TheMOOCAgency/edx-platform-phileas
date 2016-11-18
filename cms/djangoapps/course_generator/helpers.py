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
from opaque_keys.edx.locations import SlashSeparatedCourseKey

from courseware.courses import get_course_by_id

from util.string_utils import _has_non_ascii_characters
from util.organizations_helpers import (
    add_organization_course,
    get_organization_by_short_name,
    organizations_enabled,
)

from contentstore.views.course import create_new_course_in_store
from openedx.core.djangoapps.models.course_details import CourseDetails

from course_generator.utils import store_jacket_image


def create_course(subject):
    """
    Creates course using the provided information.

    Argument: subject dictionary

    Author: Naresh Makwana
    """
    try:
        org = "Vodeclic"
        course = subject.get('id')
        display_name = subject.get('title')
        # force the start date for reruns and allow us to override start via the client
        publish_date = "2000-01-01"
        end_date = "2050-12-31"
        end_datetime = CourseFields.end.default
        publish_datetime = CourseFields.start.default
        try:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            publish_datetime = datetime.strptime(publish_date, '%Y-%m-%d')
        except:
            pass
        start = publish_datetime
        end = end_datetime
        run = '2000_T2'

        # allow/disable unicode characters in course_id according to settings
        if not settings.FEATURES.get('ALLOW_UNICODE_COURSE_ID'):
            if _has_non_ascii_characters(org) or _has_non_ascii_characters(course) or _has_non_ascii_characters(run):
                return

        fields = {
            'start': start,
            'end':end,
            'enrollment_start':start,
            'enrollment_end': end,
        }
        if display_name is not None:
            fields['display_name'] = display_name

        # Set a unique wiki_slug for newly created courses. To maintain active wiki_slugs for
        # existing xml courses this cannot be changed in CourseDescriptor.
        # # TODO get rid of defining wiki slug in this org/course/run specific way and reconcile
        # w/ xmodule.course_module.CourseDescriptor.__init__
        wiki_slug = u"{0}.{1}.{2}".format(org, course, run)
        definition_data = {'wiki_slug': wiki_slug}
        fields.update(definition_data)

        _create_new_course(subject, org, course, run, fields)

    except DuplicateCourseError:
        return
    except InvalidKeyError:
        return

def _create_new_course(subject, org, number, run, fields):
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
    try:
        new_course = create_new_course_in_store(store_for_new_course, user, org, number, run, fields)

    except DuplicateCourseError:
        existing_course_key = SlashSeparatedCourseKey.from_deprecated_string('course-v1:'+org+'+'+number+'+'+run)
        new_course = get_course_by_id(existing_course_key)

    add_organization_course(org_data, new_course.id)

    # Set description and images for the course
    course_image_name, course_image_asset_path = store_jacket_image(
        new_course.id, settings.VODECLIC_COURSE_IMAGE_LOCATION,
        subject.get("id") + ".png"
    )
    additional_info = {
        'display_name': subject.get('title'),
        'language': subject.get('language', 'fr'),
        'short_description': subject.get('description', ''),
        'intro_video': None,
        'course_image_name': course_image_name,
        'course_image_asset_path': course_image_asset_path,
        'start_date': new_course.start,
        'end_date': new_course.end,
        'enrollment_start': new_course.start,
        'enrollment_end': new_course.end
    }

    CourseDetails.update_from_json(new_course.id, additional_info, user)
