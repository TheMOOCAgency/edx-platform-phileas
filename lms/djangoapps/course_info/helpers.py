"""
Course info helpers
"""
from edxmako.shortcuts import render_to_string
from xmodule.modulestore.django import modulestore
from courseware.module_render import get_module_for_descriptor, _add_timed_exam_info
from courseware.model_data import FieldDataCache, ScoresClient
from util import milestones_helpers
from openedx.core.lib.gating import api as gating_api
from courseware.entrance_exams import user_must_complete_entrance_exam
from util.model_utils import slugify
from django.core.context_processors import csrf
from django.contrib.auth.models import User
from util.db import outer_atomic
from courseware import grades


def prepare_chapters_with_grade(student, request, course):
    '''
    Create chapters with grade details.

    Return format:
    { 'chapters': [
            {'display_name': name, 'sections': SECTIONS},
        ],
    }

    where SECTIONS is a list
    [ {'display_name': name, 'format': format, 'due': due, 'completed' : bool,
        'graded': bool}, ...]

    chapters with name 'hidden' are skipped.

    NOTE: assumes that if we got this far, user has access to course.  Returns
    [] if this is not the case.
    '''
    with outer_atomic():
        field_data_cache = grades.field_data_cache_for_grading(course, student)
        scores_client = ScoresClient.from_field_data_cache(field_data_cache)

    courseware_summary = grades.progress_summary(
        student, request, course, field_data_cache=field_data_cache, scores_client=scores_client
    )

    # find the passing grade for the course
    nonzero_cutoffs = [cutoff for cutoff in course.grade_cutoffs.values() if cutoff > 0]
    success_cutoff = min(nonzero_cutoffs) if nonzero_cutoffs else None

    chapters = []
    section_index = 0
    for chapter in courseware_summary:
        if not chapter['display_name'] == "hidden":
            sections = []
            for section in chapter['sections']:
                section_index += 1
                earned = section['section_total'].earned
                total = section['section_total'].possible
                percentage = earned * 100 / total if earned > 0 and total > 0 else 0
                sections.append({
                    'section_index': section_index,
                    'display_name': section['display_name'],
                    'passed': success_cutoff and percentage >= success_cutoff
                })
            chapters.append({
                'display_name': chapter['display_name'],
                'sections': sections
            })

    return chapters

def render_accordion(request, course, table_of_contents):
    """
    Returns the HTML that renders the navigation for the given course.
    Expects the table_of_contents to have data on each chapter and section,
    including which ones are completed.
    """
    context = dict(
        [
            ('toc', table_of_contents),
            ('course_id', unicode(course.id)),
            ('csrf', csrf(request)['csrf_token']),
        ]
    )
    return render_to_string('course_info/accordion.html', context)

def inject_custom_accordian_into_context(context, user, request, course):
        # get the custom accordian to be shown on course home
        chapters = prepare_chapters_with_grade(user, request, course)
        context['accordion'] = render_accordion(request, course, chapters)
