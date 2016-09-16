"""
TMA platform wide news APIs

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

from news.models import NewsPage


class APINewsPages(APIView):
    """
        **Use Cases**

            Get the platform wide news.
            Can get news by Id as well by range.

        **Example Requests**

            GET /api/news/<news_id>/
            GET /api/news/?n=5
            GET /api/news/?user_defined_order=1
            GET /api/news/?n=2&user_defined_order=1

                REQUEST PARAMS:
                    'n': <How many news>,  # default is 5
                    'user_defined_order': <0 | 1> # if 0 order by date

        **Response Values**

            If no such news exists with the specified ID, an HTTP 400 "Bad
            Request" response is returned.

            If requested page is not visible then as HTTP 403 "Forbidden" response if returned.

            Else, The HTTP 200 response will be returned with following format:
            When no news_id is provided
            {
                'news': [
                    {
                        'news_id': <news-id>,
                        'title': <news-title>,
                        'summary': <news-summary>,
                        'jacket': <news jacket url>,
                        'published_on': <news create date>,
                        'author': <news author name>
                    },....
                ]
            }
            When news id is provided
            {
                'news_id': <news-id>,
                'title': <news-title>,
                'summary': <news-summary>,
                'jacket': <news jacket url>,
                'published_on': <news create date>,
                'author': <news author name>
            }
    """
    authentication_classes = (
        OAuth2AuthenticationAllowInactiveUser, SessionAuthenticationAllowInactiveUser, JwtAuthentication
    )
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, news_id=None):
        if news_id:
            try:
                news = NewsPage.objects.get(pk=news_id)
            except NewsPage.DoesNotExist:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        'error_code': 'news_id_not_valid'
                    }
                )
            if not news.visible:
                return Response(
                    status=status.HTTP_403_FORBIDDEN,
                    data={
                        'error_code': 'news_not_visible'
                    }
                )
            return Response(
                data={
                    'news_id': news.id,
                    'title': news.title,
                    'summary': news.content,
                    'jacket': '',
                    'published_on': news.created.strftime("%d %B %Y"),
                    'author': news.author.username
                }
            )
        else:  # requested news in bulk
            user_defined_order = int(request.GET.get('user_defined_order', 0))
            n_pages =  int(request.GET.get('n', 5))
            news = NewsPage.objects.filter(visible=True).order_by('-modified')
            if user_defined_order:
                news = sorted(news, key=lambda x: x.order_num)
            news_json = []
            for page in news[:n_pages]:
                news_json.append({
                    'news': page.id,
                    'title': page.title,
                    'summary': page.content,
                    'jacket': '',
                    'published_on': page.created.strftime("%d %B %Y"),
                    'author': page.author.username
                })

            return Response(
                data={
                    'news': news_json
                }
            )
