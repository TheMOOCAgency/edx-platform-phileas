"""
Views related to news pages
"""
from util.json_request import expect_json, JsonResponse

from django.http import HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from edxmako.shortcuts import render_to_response

from news.models import NewsPage
from news.pages import create_page, save_page, delete_page
from news.utils import get_lms_link_for_news


@login_required
@ensure_csrf_cookie
@require_http_methods(("GET"))
def news_outline(request):
    """
    The restful handler for news outline.
    Called to list at CMS.

    Author: Naresh Makwana
    """
    if not request.user.is_staff:
        raise PermissionDenied()

    # assume html
    # get all pages from the news pages list
    # present in the LIFO order
    pages_to_render = NewsPage.objects.filter(
        author=request.user
    ).order_by('-modified')

    return render_to_response('edit-news.html', {
        'pages_to_render': pages_to_render,
        'lms_link': get_lms_link_for_news(),
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

@login_required
@ensure_csrf_cookie
@require_http_methods(("GET"))
def news_detail(request, page_id=None):
    """
    To make the content of the page visible
    To the student.
    """
    content = """<p class="error">Either you don't
    have the permission to acccess the content of the page OR
    the requested page does not exists</p>
    """
    title = ''

    try:
        page = NewsPage.objects.get(pk=page_id)
        if page.visible or request.user.is_staff:
            content = page.content
            title = page.title
    except NewsPage.DoesNotExist:
        pass

    return render_to_response('static_templates/platform_wide_news_detail.html', {
        'content': content,
        'title': title
    })

@login_required
@ensure_csrf_cookie
@require_http_methods(("GET"))
def news(request):
    """
    List the news on LMS with pagination.
    """
    # Get all news
    news_list = NewsPage.objects.all()

    # Filter if its needs to be accessed by student
    if not request.user.is_staff:
        news_list = news_list.filter(visible=True)

    # Apply Order by
    news_list = news_list.order_by('-modified')

    # Show 5 news per page
    paginator = Paginator(news_list, 5)

    # Get page number from request
    page = request.GET.get('page')

    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        news = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        news = paginator.page(paginator.num_pages)

    # Render news list
    return render_to_response('static_templates/platform_wide_news.html', {
        'news_list': news
    })
