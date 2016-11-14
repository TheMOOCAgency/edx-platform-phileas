"""
Api for getting the number of messages posted on the forum by a user

Author: Chintan Joshi
"""
from rest_framework.response import Response
from rest_framework.views import APIView
from openedx.core.lib.api.view_utils import view_auth_classes
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from opaque_keys import InvalidKeyError

from lms.lib.comment_client.thread import Thread
from courseware.courses import get_course_by_id
from discussion_api.views import ThreadViewSet
from discussion_api.api import (
    get_course,
    get_thread,
)
from courseware.module_render import get_module_for_descriptor
from discussion_api.views import CommentViewSet, ThreadViewSet
from xmodule.modulestore.django import modulestore

@view_auth_classes()
class APIForumMessages(APIView):
    """
        **Use Cases**

            Retrieve count of comments made by user in a discussion of specified section.

        **Example Requests**:

            GET: /forum_messages/course_id/section_id
        
            GET: /forum_messages/course-v1:test+test111+2014_T3/5eb8a906ce894b12b0363465327d8476/

        **Returns**:

            Course_id: id of the course

            Section_id: id of the section

            User: current user

            Comment Count: Total number of comments done by the user in a discussion of specified section

        **Errors**:

        Errors are thrown in following cases
        
        1: User is not allwoed to do the operation: 
        
            - Either the user is not logged in
        
            - Or the user is not enrolled in the course
        
            - Course is restricted
        
        2: Course has no active discussion:
        
            - Course is not having any discussion in the chapter/section part
        
            - Discussion are not visible
        
        3: section_id does not exist:
        
            - Wrong input of section id
    """
    def get(self, request, course_id, section_id):
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

        commentable_id_list = []
        for chapter in course_module.get_children():
            for section in chapter.get_children():
                if section_id == section.url_name:
                    for unit in section.get_children():
                        for vertical in unit.get_children():
                            if vertical.category == 'discussion':
                                commentable_id_list.append(vertical.discussion_id)
                    break



        count = 0
        for cid in commentable_id_list:
            query_params = {
            "course_id":course_id,
            "user_id": request.user.id,
            "commentable_id": cid
            }
            threads = Thread.search(query_params).collection
            for thread in threads:
                if thread['thread_type'] == "discussion":
                    request.GET = {'thread_id': thread['id']}
                elif thread['thread_type'] == "question":
                    request.GET = {'thread_id': thread['id'],'endorsed':False}
                else:
                    pass
                if thread['username'] == request.user.username:
                    count = count + 1 
                list_comments = CommentViewSet()
                comments = list_comments.list(request).data
                for comment in comments['results']:
                    if comment['author'] == request.user.username:
                        count = count + 1

                    if comment['child_count'] > 0:
                        child_comments = list_comments.retrieve(
                            request, comment_id=comment['id']
                        ).data
                        for child_comment in child_comments['results']:
                            if child_comment['author'] == request.user.username:
                                count = count + 1
            return Response(
                data = {
                "Course_id": course_id,
                "Section_id": section_id,
                "User":request.user.username,
                "Comment Count": count,

            })
        else:
            return Response(
                data={
                "Error":"No active discussion for given section_id"
            })
