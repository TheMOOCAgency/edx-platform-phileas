"""
View which gets the list of section_id in which a user has commented

Author: Chintan Joshi
"""
from lms.lib.comment_client.thread import Thread
from student.models import User
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from courseware.courses import get_course_by_id
from courseware.module_render import get_module_for_descriptor

from xmodule.modulestore.django import modulestore


def get_section_list(request,course_id,student_id):
    section_id_list = []
    commentable_id_list = []
    try:
        course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    except Exception as e:
        return Resposne(
            data={
            "Error": e.message
        })

    course = get_course_by_id(course_key)
    with modulestore().bulk_operations(course.id):
        course_module = get_module_for_descriptor(
            request.user, request, course, None, course.id, course=course
        )
        if course_module is None:
            return Response(
                data={
                "Error":"User is not allowed to do the operation"
            })

    student = User.objects.get(id=student_id)
    query_params = {
    "course_id":course_id,
    "user_id": student.id,
    }
    threads = Thread.search(query_params).collection

    for chapter in course_module.get_children():
        for section in chapter.get_children():
            for unit in section.get_children():
                for vertical in unit.get_children():
                    if vertical.category == 'discussion':
                        for thread in threads:
                            if thread['commentable_id'] == vertical.discussion_id and thread['username'] == student.username:
                                section_id_list.append(section.url_name)
                break

    return section_id_list