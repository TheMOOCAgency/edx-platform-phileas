"""
Course info helpers
"""
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from edxmako.shortcuts import render_to_string
from xmodule.modulestore.django import modulestore
from openedx.core.lib.gating import api as gating_api

from courseware.module_render import (
    get_module_for_descriptor,
    _add_timed_exam_info,
    get_module_by_usage_id
)
from courseware.model_data import FieldDataCache, ScoresClient
from courseware.entrance_exams import user_must_complete_entrance_exam
from courseware import grades

from util import milestones_helpers
from util.db import outer_atomic
from util.model_utils import slugify

from forum_messages.views import get_section_list as get_discussions_participated
from course_progress.models import StudentCourseProgress


def prepare_sections_with_grade(request, course):
    '''
    Create sections with grade details.

    Return format:
    {
        'sections': [
            {
                'display_name': name,
                # in case of cohorts or any other accessibility settings
                'hidden': hidden,
                'url_name': url_name,
                'units': UNITS,
                'rank': rank,
                'badge': bagde status,
                'points': grade points,
                'podium': podium status,
                'week': section_index + 1,
            },
        ],
    }

    where UNITS is a list
    [
        {
            'display_name': name,
            'position': unit position in section,
            'css_class': css class,
        }
        , ...
    ]

    sections with name 'hidden' are skipped.

    NOTE: assumes that if we got this far, user has access to course.  Returns
    [] if this is not the case.
    '''
    # Set the student to request user
    student = request.user

    # Get the field data cache
    field_data_cache = FieldDataCache.cache_for_descriptor_descendents(
        course.id, student, course, depth=2,
    )
    
    # Get the course module
    with modulestore().bulk_operations(course.id):
        course_module = get_module_for_descriptor(
            student, request, course, field_data_cache, course.id, course=course
        )
        if course_module is None:
            return []

    # Get the field data cache
    staff_user = User.objects.filter(is_staff=1)[0]
    staff_field_data_cache = FieldDataCache.cache_for_descriptor_descendents(
        course.id, staff_user, course, depth=2,
    )

    # Get the course module
    with modulestore().bulk_operations(course.id):
        staff_course_module = get_module_for_descriptor(
            staff_user, request, course, staff_field_data_cache, course.id, course=course
        )

    # staff accessible chapters
    staff_chapters = staff_course_module.get_display_items()

    # find the passing grade for the course
    nonzero_cutoffs = [cutoff for cutoff in course.grade_cutoffs.values() if cutoff > 0]
    success_cutoff = min(nonzero_cutoffs) if nonzero_cutoffs else 0

    # find the course progress
    progress = get_course_progress(student, course.id)

    # prepare a list of discussions participated by user
    discussions_participated = get_discussions_participated(
        request,
        course.id.to_deprecated_string(),
        student.id
    )

    # get courseware summary
    with outer_atomic():
        field_data_cache = grades.field_data_cache_for_grading(course, student)
        scores_client = ScoresClient.from_field_data_cache(field_data_cache)

    courseware_summary = grades.progress_summary(
        student, request, course, field_data_cache=field_data_cache, scores_client=scores_client
    )

    section_grades = {}
    for section in courseware_summary:
        earned = 0
        total = 0
        for sub_section in section['sections']:
            earned += sub_section['section_total'].earned
            total += sub_section['section_total'].possible

        section_score = earned / total if earned > 0 and total > 0 else 0
        section_grades[section['url_name']] = {
            'earned': earned,
            'total': total,
            'css_class': ('text-red', 'text-green')[int(section_score >= 0.6)] if total > 0 else ''
        }

    # Check for content which needs to be completed
    # before the rest of the content is made available
    required_content = milestones_helpers.get_required_content(course, student)

    # Check for gated content
    gated_content = gating_api.get_gated_content(course, student)

    # The user may not actually have to complete the entrance exam, if one is required
    if not user_must_complete_entrance_exam(request, student, course):
        required_content = [content for content in required_content if not content == course.entrance_exam_id]

    sections = list()
    student_chapters = course_module.get_display_items()
    urlname_chapters = {}
    for student_chap in student_chapters:
        urlname_chapters.update({student_chap.url_name:student_chap})
    final_chapters = {}
    for chapter_index, chapter in enumerate(staff_chapters):
        fin_chap = urlname_chapters.get(chapter.url_name)
        if fin_chap:
            final_chapters.update({str(chapter_index+1):{'hidden': False, 'chapter':fin_chap}})
        else:
            final_chapters.update({str(chapter_index+1):{'hidden':True}})

    for section_index, chapter_info in final_chapters.items():
        # Mark as hidden and Skip the current chapter if a hide flag is tripped
        if chapter_info['hidden']:
            sections.append({
                'hidden': True,
                'week': "WEEK {week}: ".format(week=section_index),
                'points': {
                    'total': 0,
                    'earned': 0,
                    'css_class': 'text-disabled'
                },
            })
            continue

        chapter = chapter_info['chapter']
        # get the points
        section_points = section_grades.get(chapter.url_name, {})

        units = list()
        for sequential in chapter.get_display_items():
            # Set hidden status of the sequential if it is gated/hidden from the user
            hidden = (
                gated_content and unicode(sequential.location) in gated_content or
                sequential.hide_from_toc
            )

            if hidden:
                continue

            for index, unit in enumerate(sequential.get_display_items()):
                css_class = 'dark-gray'
                if unit.graded:
                    total_excercises = 0
                    attempted_excercises = 0
                    unit_max_score = 0
                    unit_score = 0
                    for component in unit.get_display_items():
                        if component.category == 'problem':
                            if component.graded:
                                total_excercises += 1
                                attempted_excercises += is_attempted_internal(
                                    str(component.location), progress
                                )
                                with modulestore().bulk_operations(course.id):
                                    capa_module, tracking_context = get_module_by_usage_id(
                                        request, course.id.to_deprecated_string(),
                                        str(component.location), course=course
                                    )
                                unit_max_score += capa_module.max_score()
                                unit_score += capa_module.get_score().get('score')

                    if total_excercises:
                        css_class = 'blue'
                        if attempted_excercises == total_excercises:
                            css_class = 'green'
                            if unit_max_score and unit_score / unit_max_score < success_cutoff:
                                css_class = 'red'

                position = index + 1  # For jumping to the unit directly
                unit_context = {
                    'display_name': unit.display_name_with_default_escaped,
                    'position': position,
                    'css_class': css_class,
                    'courseware_url': reverse(
                        'courseware_position',
                        args=[
                            course.id,
                            chapter.url_name,
                            sequential.url_name,
                            position
                        ]
                    )
                }
                units.append(unit_context)

        section_context = {
            'display_name': chapter.display_name_with_default_escaped,
            'url_name': chapter.url_name,
            'hidden': False,
            'rank': 1,
            'competency': int(section_points.get('earned')) == int(section_points.get('total')),
            'points': {
                'total': int(section_points.get('total')),
                'earned': int(section_points.get('earned')),
                'css_class': section_points.get('css_class')
            },
            'participation': chapter.url_name in discussions_participated,
            'units': units,
            'week': "WEEK {week}: ".format(week=section_index),
        }
        sections.append(section_context)

    return sections

def is_attempted_internal(capa_module_id, course_progress):
    """
    Problem needs to be considered as attempted:
        If  has checked the problem.

    Returns 1 if attempted else 0

    Author: Naresh Makwana
    """
    capa_module_progress = course_progress.get(capa_module_id, {})
    is_attempted = int(int(capa_module_progress.get('progress', 0)) == 100)

    return is_attempted

def get_course_progress(student, course_key):
    progress = {}

    try:
        course_progress = StudentCourseProgress.objects.get(student=student.id, course_id=course_key)
        progress = course_progress.progress
    except StudentCourseProgress.DoesNotExist:
        pass

    return progress
