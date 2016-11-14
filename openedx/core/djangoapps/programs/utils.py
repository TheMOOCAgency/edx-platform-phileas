# -*- coding: utf-8 -*-
"""Helper functions for working with Programs."""
import datetime
import logging

from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from opaque_keys.edx.keys import CourseKey
import pytz

from lms.djangoapps.certificates.api import get_certificates_for_user, is_passing_status
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.programs.models import ProgramsApiConfig
from openedx.core.lib.edx_api_utils import get_edx_api_data
from student.models import CourseEnrollment
from xmodule.course_metadata_utils import DEFAULT_START_DATE


log = logging.getLogger(__name__)


def get_programs(user, program_id=None):
    """Given a user, get programs from the Programs service.
    Returned value is cached depending on user permissions. Staff users making requests
    against Programs will receive unpublished programs, while regular users will only receive
    published programs.

    Arguments:
        user (User): The user to authenticate as when requesting programs.

    Keyword Arguments:
        program_id (int): Identifies a specific program for which to retrieve data.

    Returns:
        list of dict, representing programs returned by the Programs service.
    """
    programs_config = ProgramsApiConfig.current()

    # Bypass caching for staff users, who may be creating Programs and want
    # to see them displayed immediately.
    cache_key = programs_config.CACHE_KEY if programs_config.is_cache_enabled and not user.is_staff else None
    return get_edx_api_data(programs_config, user, 'programs', resource_id=program_id, cache_key=cache_key)


def flatten_programs(programs, course_ids):
    """Flatten the result returned by the Programs API.

    Arguments:
        programs (list): Serialized programs
        course_ids (list): Course IDs to key on.

    Returns:
        dict, programs keyed by course ID
    """
    flattened = {}

    for program in programs:
        try:
            for course_code in program['course_codes']:
                for run in course_code['run_modes']:
                    run_id = run['course_key']
                    if run_id in course_ids:
                        flattened.setdefault(run_id, []).append(program)
        except KeyError:
            log.exception('Unable to parse Programs API response: %r', program)

    return flattened


def get_programs_for_dashboard(user, course_keys):
    """Build a dictionary of programs, keyed by course.

    Given a user and an iterable of course keys, find all the programs relevant
    to the user's dashboard and return them in a dictionary keyed by course key.

    Arguments:
        user (User): The user to authenticate as when requesting programs.
        course_keys (list): List of course keys representing the courses in which
            the given user has active enrollments.

    Returns:
        dict, containing programs keyed by course. Empty if programs cannot be retrieved.
    """
    programs_config = ProgramsApiConfig.current()
    course_programs = {}

    if not programs_config.is_student_dashboard_enabled:
        log.debug('Display of programs on the student dashboard is disabled.')
        return course_programs

    programs = get_programs(user)
    if not programs:
        log.debug('No programs found for the user with ID %d.', user.id)
        return course_programs

    course_ids = [unicode(c) for c in course_keys]
    course_programs = flatten_programs(programs, course_ids)

    return course_programs


def get_programs_for_credentials(user, programs_credentials):
    """ Given a user and an iterable of credentials, get corresponding programs
    data and return it as a list of dictionaries.

    Arguments:
        user (User): The user to authenticate as for requesting programs.
        programs_credentials (list): List of credentials awarded to the user
            for completion of a program.

    Returns:
        list, containing programs dictionaries.
    """
    certificate_programs = []

    programs = get_programs(user)
    if not programs:
        log.debug('No programs for user %d.', user.id)
        return certificate_programs

    for program in programs:
        for credential in programs_credentials:
            if program['id'] == credential['credential']['program_id']:
                program['credential_url'] = credential['certificate_url']
                certificate_programs.append(program)

    return certificate_programs


def get_display_category(program):
    """ Given the program, return the category of the program for display
    Arguments:
        program (Program): The program to get the display category string from

    Returns:
        string, the category for display to the user.
        Empty string if the program has no category or is null.
    """
    display_candidate = ''
    if program and program.get('category'):
        if program.get('category') == 'xseries':
            display_candidate = 'XSeries'
        else:
            display_candidate = program.get('category', '').capitalize()
    return display_candidate


def get_completed_courses(student):
    """
    Determine which courses have been completed by the user.

    Args:
        student:
            User object representing the student

    Returns:
        iterable of dicts with structure {'course_id': course_key, 'mode': cert_type}

    """
    all_certs = get_certificates_for_user(student.username)
    return [
        {'course_id': unicode(cert['course_key']), 'mode': cert['type']}
        for cert in all_certs
        if is_passing_status(cert['status'])
    ]


class ProgramProgressMeter(object):
    """Utility for gauging a user's progress towards program completion.

    Arguments:
        user (User): The user for which to find programs.
    """
    def __init__(self, user):
        self.user = user
        self.course_ids = None

        self.programs = get_programs(self.user)
        self.course_certs = get_completed_courses(self.user)

    @cached_property
    def engaged_programs(self):
        """Derive a list of programs in which the given user is engaged.

        Returns:
            list of program dicts, ordered by most recent enrollment.
        """
        enrollments = CourseEnrollment.enrollments_for_user(self.user)
        enrollments = sorted(enrollments, key=lambda e: e.created, reverse=True)
        # enrollment.course_id is really a course key ಠ_ಠ
        self.course_ids = [unicode(e.course_id) for e in enrollments]

        flattened = flatten_programs(self.programs, self.course_ids)

        engaged_programs = []
        for course_id in self.course_ids:
            for program in flattened.get(course_id, []):
                if program not in engaged_programs:
                    engaged_programs.append(program)

        return engaged_programs

    @property
    def progress(self):
        """Gauge a user's progress towards program completion.

        Returns:
            list of dict, each containing information about a user's progress
                towards completing a program.
        """
        progress = []
        for program in self.engaged_programs:
            completed, in_progress, not_started = [], [], []

            for course_code in program['course_codes']:
                name = course_code['display_name']

                if self._is_course_code_complete(course_code):
                    completed.append(name)
                elif self._is_course_code_in_progress(course_code):
                    in_progress.append(name)
                else:
                    not_started.append(name)

            progress.append({
                'id': program['id'],
                'completed': completed,
                'in_progress': in_progress,
                'not_started': not_started,
            })

        return progress

    @property
    def completed_programs(self):
        """Identify programs completed by the student.

        Returns:
            list of int, each the ID of a completed program.
        """
        return [program['id'] for program in self.programs if self._is_program_complete(program)]

    def _is_program_complete(self, program):
        """Check if a user has completed a program.

        A program is completed if the user has completed all nested course codes.

        Arguments:
            program (dict): Representing the program whose completion to assess.

        Returns:
            bool, whether the program is complete.
        """
        return all(self._is_course_code_complete(course_code) for course_code in program['course_codes'])

    def _is_course_code_complete(self, course_code):
        """Check if a user has completed a course code.

        A course code is completed if the user has earned a certificate
        in the right mode for any nested run.

        Arguments:
            course_code (dict): Containing nested run modes.

        Returns:
            bool, whether the course code is complete.
        """
        return any(self._parse(run_mode) in self.course_certs for run_mode in course_code['run_modes'])

    def _is_course_code_in_progress(self, course_code):
        """Check if a user is in the process of completing a course code.

        A user is in the process of completing a course code if they're
        enrolled in the course.

        Arguments:
            course_code (dict): Containing nested run modes.

        Returns:
            bool, whether the course code is in progress.
        """
        return any(run_mode['course_key'] in self.course_ids for run_mode in course_code['run_modes'])

    def _parse(self, run_mode):
        """Modify the structure of a run mode dict.

        Arguments:
            run_mode (dict): With `course_key` and `mode_slug` keys.

        Returns:
            dict, with `course_id` and `mode` keys.
        """
        parsed = {
            'course_id': run_mode['course_key'],
            'mode': run_mode['mode_slug'],
        }

        return parsed


def supplement_program_data(program_data, user):
    """Supplement program course codes with CourseOverview and CourseEnrollment data.

    Arguments:
        program_data (dict): Representation of a program.
        user (User): The user whose enrollments to inspect.
    """
    for course_code in program_data['course_codes']:
        for run_mode in course_code['run_modes']:
            course_key = CourseKey.from_string(run_mode['course_key'])
            course_overview = CourseOverview.get_from_id(course_key)

            run_mode['course_url'] = reverse('course_root', args=[course_key])
            run_mode['course_image_url'] = course_overview.course_image_url

            human_friendly_format = '%x'
            start_date = course_overview.start or DEFAULT_START_DATE
            end_date = course_overview.end or datetime.datetime.max.replace(tzinfo=pytz.UTC)
            run_mode['start_date'] = start_date.strftime(human_friendly_format)
            run_mode['end_date'] = end_date.strftime(human_friendly_format)

            run_mode['is_enrolled'] = CourseEnrollment.is_enrolled(user, course_key)

            enrollment_start = course_overview.enrollment_start or datetime.datetime.min.replace(tzinfo=pytz.UTC)
            enrollment_end = course_overview.enrollment_end or datetime.datetime.max.replace(tzinfo=pytz.UTC)
            is_enrollment_open = enrollment_start <= timezone.now() < enrollment_end
            run_mode['is_enrollment_open'] = is_enrollment_open

            # TODO: Currently unavailable on LMS.
            run_mode['marketing_url'] = ''

    return program_data
