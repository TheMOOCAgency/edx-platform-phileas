"""
Views related to news pages
"""
from util.json_request import expect_json, JsonResponse

from django.http import HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from edxmako.shortcuts import render_to_response

from news.models import NewsPage
from news.pages import create_page, save_page, delete_page
from news.utils import get_lms_link_for_page


@login_required
@ensure_csrf_cookie
@require_http_methods(("GET"))
def news_outline(request):
    """
    The restful handler for news outline.

    DELETE
        To delete any news page
    PUT or POST
        save the pages

    Creating a page, deleting a page, or changing its contents is not supported through this method.
    Instead use pages.page_handler
    """
    if not request.user.is_staff:
        raise PermissionDenied()

    # assume html
    # get all pages from the news pages list
    # present in the LIFO order
    pages_to_render = NewsPage.objects.filter(author=request.user)

    return render_to_response('edit-news.html', {
        'pages_to_render': pages_to_render,
        'lms_link': get_lms_link_for_page(),
    })

@expect_json
@login_required
@ensure_csrf_cookie
@require_http_methods(("DELETE", "PUT", "POST", "PATCH"))
def news_handler(request, page_id=None):
    """
    The restful handler news.

    DELETE
        To delete any news page
    PUT or POST
        save the pages
    """
    # Must have staff access
    if not request.user.is_staff:
        raise PermissionDenied()

    # For updating any page, page ID is must
    if page_id:
        try:
            page = NewsPage.objects.get(pk=page_id)
        except NewsPage.DoesNotExist:
            return JsonResponse({
                'error': 'No such page exists.'
            })

        # Staff can access own pages
        if not page.access_check(request.user):
            raise PermissionDenied()

        if request.method == 'DELETE':
            delete_page(page)
        elif request.method in ('PUT', 'POST'):
            save_page(page, request.json)

        return JsonResponse()
    else:  # no page ID
        if request.method == 'POST':
            page = create_page(request.user)
            return JsonResponse({
                'page_id': page.id
            })
        else:
            return JsonResponse({
                'error': 'Only page create allowed without page ID.'
            })

@expect_json
@login_required
@ensure_csrf_cookie
@require_http_methods(("GET"))
def get_news_content(request, page_id=None):
    """
    To get the content for the specified
    page.

    Returns content if page exists and no
    errors. Else return ''
    """
    # Initialize the response dictionary
    content = ''

    # Must have staff access
    if not request.user.is_staff:
        raise PermissionDenied()

    # For updating any page, page ID is must
    if page_id:
        try:
            page = NewsPage.objects.get(pk=page_id)
            content = page.content
        except NewsPage.DoesNotExist:
            pass

    # Return JSON response
    return JsonResponse({
        'content': content
    })
