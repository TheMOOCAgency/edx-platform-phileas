"""
Course info helpers
"""
from edxmako.shortcuts import render_to_string
from xmodule.modulestore.django import modulestore
from courseware.module_render import get_module_for_descriptor, _add_timed_exam_info
from courseware.model_data import FieldDataCache
from util import milestones_helpers
from openedx.core.lib.gating import api as gating_api
from courseware.entrance_exams import user_must_complete_entrance_exam
from util.model_utils import slugify
from django.core.context_processors import csrf


def toc_for_course(user, request, course):
    '''
    Create a table of contents from the module store

    Return format:
    { 'chapters': [
            {'display_name': name, 'url_name': url_name, 'sections': SECTIONS},
        ],
    }

    where SECTIONS is a list
    [ {'display_name': name, 'url_name': url_name,
       'format': format, 'due': due, 'completed' : bool, 'graded': bool}, ...]

    chapters with name 'hidden' are skipped.

    NOTE: assumes that if we got this far, user has access to course.  Returns
    None if this is not the case.
    '''

    field_data_cache = FieldDataCache.cache_for_descriptor_descendents(
        course.id, user, course, 2,
    )
    with modulestore().bulk_operations(course.id):
        course_module = get_module_for_descriptor(
            user, request, course, field_data_cache, course.id, course=course
        )
        if course_module is None:
            return {'chapters': {}}

        toc_chapters = list()
        chapters = course_module.get_display_items()

        # Check for content which needs to be completed
        # before the rest of the content is made available
        required_content = milestones_helpers.get_required_content(course, user)

        # Check for gated content
        gated_content = gating_api.get_gated_content(course, user)

        # The user may not actually have to complete the entrance exam, if one is required
        if not user_must_complete_entrance_exam(request, user, course):
            required_content = [content for content in required_content if not content == course.entrance_exam_id]

        section_index = 0
        for chapter in chapters:
            # Only show required content, if there is required content
            # chapter.hide_from_toc is read-only (bool)
            display_id = slugify(chapter.display_name_with_default_escaped)
            local_hide_from_toc = False
            if required_content:
                if unicode(chapter.location) not in required_content:
                    local_hide_from_toc = True

            # Skip the current chapter if a hide flag is tripped
            if chapter.hide_from_toc or local_hide_from_toc:
                continue

            sections = list()
            for section in chapter.get_display_items():
                section_index += 1
                # skip the section if it is gated/hidden from the user
                if gated_content and unicode(section.location) in gated_content:
                    continue
                if section.hide_from_toc:
                    continue

                # check whether the user has completed the section or not
                is_section_completed = True  # TODO: Naresh, test with grade for the section
                section_context = {
                    'display_name': section.display_name_with_default_escaped,
                    'url_name': section.url_name,
                    'format': section.format if section.format is not None else '',
                    'due': section.due,
                    'completed': is_section_completed,
                    'graded': section.graded,
                    'section_index': section_index,
                }
                _add_timed_exam_info(user, course, section, section_context)


                sections.append(section_context)

            toc_chapters.append({
                'display_name': chapter.display_name_with_default_escaped,
                'display_id': display_id,
                'url_name': chapter.url_name,
                'sections': sections,
            })
        return {
            'chapters': toc_chapters,
        }

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
        table_of_contents = toc_for_course(user, request, course)
        context['accordion'] = render_accordion(request, course, table_of_contents['chapters'])
