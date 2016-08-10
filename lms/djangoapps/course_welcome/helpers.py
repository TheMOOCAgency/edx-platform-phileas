"""
Course info helpers
"""
from django.core.context_processors import csrf
from django.contrib.auth.models import User

from edxmako.shortcuts import render_to_string
from xmodule.modulestore.django import modulestore
from openedx.core.lib.gating import api as gating_api

from courseware.module_render import get_module_for_descriptor, _add_timed_exam_info
from courseware.model_data import FieldDataCache, ScoresClient
from courseware.entrance_exams import user_must_complete_entrance_exam
from courseware.views.views import get_current_child
from courseware import grades

from util import milestones_helpers
from util.db import outer_atomic
from util.model_utils import slugify


def prepare_chapters_with_grade(request, course):
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
    student = request.user

    with outer_atomic():
        field_data_cache = grades.field_data_cache_for_grading(course, student)
        scores_client = ScoresClient.from_field_data_cache(field_data_cache)

    courseware_summary = grades.progress_summary(
        student, request, course, field_data_cache=field_data_cache, scores_client=scores_client
    )

    # find the passing grade for the course
    nonzero_cutoffs = [cutoff for cutoff in course.grade_cutoffs.values() if cutoff > 0]
    success_cutoff = min(nonzero_cutoffs) * 100 if nonzero_cutoffs else 0

    # get the courseware position where left off
    active_section = None
    if course.has_children_at_depth(2):
        active_chapter = get_last_accessed_chapter(course)
        active_section = get_last_accessed_section(active_chapter)

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
                    'url_name': section['url_name'],
                    'passed': success_cutoff and percentage >= success_cutoff,
                    'paused': active_section and (section['url_name'] == active_section.url_name)
                })
            chapters.append({
                'display_name': chapter['display_name'],
                'url_name': chapter['url_name'],
                'sections': sections
            })

    return chapters

def render_accordion(request, course):
    """
    Returns the HTML that renders the navigation for the given course.
    Expects the table_of_contents to have data on each chapter and section,
    including which ones are completed.
    """
    context = {
        'chapters': prepare_chapters_with_grade(request, course),
        'course_id': unicode(course.id),
        'csrf': csrf(request)['csrf_token'],
    }

    return render_to_string('course_welcome/accordion.html', context)

def get_final_score(request, course):
    """
    To get the final score for the user in
    particular course.
    """
    grade_summary = {}
    student = request.user

    try:
        grade_summary = grades.grade(student, request, course)
    except:
        pass

    final_grade = grade_summary.get('percent', 0)

    return int(final_grade * 100)

def get_last_accessed_chapter(course):
    """
    It returns the last accessed chapter in
    the course.
    """
    return get_current_child(course, min_depth=1, requested_child=None)

def get_last_accessed_section(chapter):
    """
    It returns the last accessed section in
    the chapter.
    """
    return get_current_child(chapter, min_depth=None, requested_child=None)

