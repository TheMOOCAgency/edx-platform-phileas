from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from seq_nav.models import StudentUnitVisit


@login_required
@ensure_csrf_cookie
@require_http_methods(["POST"])
def save_unit_visit(request):
    """
    Author: Naresh Makwana
    """
    unit_id = request.POST.get('unit_id')

    student_visit, created = StudentUnitVisit.objects.get_or_create(
        unit_id=unit_id, student = request.user
    )
    student_visit.visited = True
    student_visit.save()

    return JsonResponse({'sucess': True})

def is_unit_visited(student_id, unit_id):
    visited = False
    try:
        obj = StudentUnitVisit.objects.get(student_id=student_id, unit_id=unit_id)
        visited = obj.visited
    except:
        pass

    return visited
