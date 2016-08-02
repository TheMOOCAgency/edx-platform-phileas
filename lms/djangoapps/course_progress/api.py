"""
TMA course progress APIs

Author: Naresh Makwana
"""
from edx_rest_framework_extensions.authentication import JwtAuthentication
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from openedx.core.lib.api.authentication import (
    SessionAuthenticationAllowInactiveUser,
    OAuth2AuthenticationAllowInactiveUser,
)

from opaque_keys.edx.locations import SlashSeparatedCourseKey
from opaque_keys import InvalidKeyError

from course_progress.models import StudentCourseProgress
from course_progress.helpers import (
    get_student_rank,
    get_leaderboard,
    make_usage_id
)


class APICompletionProgress(APIView):
    """
        **Use Cases**

            Get the course completion progress of the user.
            Can get the progress for course, section, sub-section or unit.

        **Example Requests**

            GET /courses/course-v1:moocagency+M101+2016_T2/completion_progress/
            GET /courses/course-v1:moocagency+M101+2016_T2/completion_progress/
                7a3c4385339c417cb64f49e5ae5c5e92/
            GET /courses/course-v1:moocagency+M101+2016_T2/completion_progress/
                7a3c4385339c417cb64f49e5ae5c5e92/
                bf76ae04ab354c74b9b79add68db5c00/
            GET /courses/course-v1:moocagency+M101+2016_T2/completion_progress/
                7a3c4385339c417cb64f49e5ae5c5e92/
                bf76ae04ab354c74b9b79add68db5c00/
                d2366d838bdc44e8bc1f66a23abc81aa/

        **Response Values**

            If course, section, sub-section or unit does not exists with the specified ID, an HTTP 400 "Bad
            Request" response is returned.

            The HTTP 200 response has the progress between 0-100.
    """
    authentication_classes = (
        OAuth2AuthenticationAllowInactiveUser, SessionAuthenticationAllowInactiveUser, JwtAuthentication
    )
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id, chapter=None, section=None, unit=None):
        """
        GET /courses/course-v1:moocagency+M101+2016_T2/completion_progress/
        GET /courses/course-v1:moocagency+M101+2016_T2/completion_progress/
            7a3c4385339c417cb64f49e5ae5c5e92/
        GET /courses/course-v1:moocagency+M101+2016_T2/completion_progress/
            7a3c4385339c417cb64f49e5ae5c5e92/
            bf76ae04ab354c74b9b79add68db5c00/
        GET /courses/course-v1:moocagency+M101+2016_T2/completion_progress/
            7a3c4385339c417cb64f49e5ae5c5e92/
            bf76ae04ab354c74b9b79add68db5c00/
            d2366d838bdc44e8bc1f66a23abc81aa/
        """
        progress = 0

        try:
            course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
            course_progress = StudentCourseProgress.objects.get(student=request.user.id, course_id=course_key)
        except InvalidKeyError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    'error_code': 'course_id_not_valid'
                }
            )
        except StudentCourseProgress.DoesNotExist:
            pass

        if course_progress:
            if unit:
                # Request for the unit progress
                usage_id = make_usage_id(course_key, 'vertical', unit)
            elif section:
                # Request for the section progress
                usage_id = make_usage_id(course_key, 'sequential', section)
            elif chapter:
                # Request for the chapter progress
                usage_id = make_usage_id(course_key, 'chapter', chapter)
            else:
                usage_id = None

            if usage_id:
                try:
                    progress = course_progress.progress[usage_id]['progress']
                except KeyError:
                    return Response(
                        status=status.HTTP_400_BAD_REQUEST,
                        data={
                            'error_code': 'block_id_not_valid'
                        }
                    )
            else:
                # Request to get course progress
                progress = course_progress.overall_progress

        return Response(
            data={
                'progress': progress
            }
        )


class APIStudentRank(APIView):
    """
        **Use Cases**

            Get the student rank on the bases of
                course completion progress.
            Also fetches the total number of enrollments,
                that usually needs to be show along with rank.

        **Example Requests**

            GET /courses/course-v1:moocagency+M101+2016_T2/completion_rank/

        **Response Values**

            If no course exists with the specified course ID, an HTTP 400 "Bad
            Request" response is returned.

            The HTTP 200 response has the rank.
    """
    authentication_classes = (
        OAuth2AuthenticationAllowInactiveUser, SessionAuthenticationAllowInactiveUser, JwtAuthentication
    )
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id):
        """
        GET /courses/course-v1:moocagency+M101+2016_T2/completion_rank/
        """
        rank = None

        try:
            course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
        except InvalidKeyError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    'error_code': 'course_id_not_valid'
                }
            )

        # get the student rank and total number of students
        student_rank, total_students = get_student_rank(request.user.id, course_key)

        return Response(
            data={
                'student_rank': student_rank,
                'total_students': total_students
            }
        )


class APILeaderBoard(APIView):
    """
        **Use Cases**

            Get the student rank on the bases of course completion progress.
            Along with the rank it also gets the useful information about
            student, like name, profile image url, completion percent.

        **Example Requests**

            GET /courses/course-v1:moocagency+M101+2016_T2/completion_leaderboard
            GET /courses/course-v1:moocagency+M101+2016_T2/completion_leaderboard/10

            If no limit (i.e. 10 in above URL) is passed then it will take top 10 students by default.

        **Response Values**

            If no course exists with the specified course ID, an HTTP 400 "Bad
            Request" response is returned.

            The HTTP 200 response has the list of the leaderboard students with rank.
    """
    authentication_classes = (
        OAuth2AuthenticationAllowInactiveUser, SessionAuthenticationAllowInactiveUser, JwtAuthentication
    )

    def get(self, request, course_id, limit=10):
        """
        GET /courses/course-v1:moocagency+M101+2016_T2/completion_leaderboard
        GET /courses/course-v1:moocagency+M101+2016_T2/completion_leaderboard/10
        """
        leaderboard = []

        try:
            course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
        except InvalidKeyError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    'error_code': 'course_id_not_valid'
                }
            )

        # get the student rank and total number of students
        leaderboard, total_students = get_leaderboard(course_key, limit)

        return Response(
            data={
                'leaderboard': leaderboard,
                'total_students': total_students
            }
        )
