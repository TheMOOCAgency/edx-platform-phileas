from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from student.models import UserTestGroup, CourseEnrollment, UserProfile
import json
import requests
import hashlib
import datetime



def get_vodeclic_href(user):

    # Ensure the user is authenticated
    if not user.is_authenticated():
        return HttpResponseForbidden()
    else:
        if settings.FEATURES.get('TMA_VODECLIC_ENABLE'):

            now = datetime.datetime.now()

            date = now.strftime("%d%m%Y")
            datess = ("10102016")
            api = 'uYUoVrzSEVityKwgNhHO'
            partenaire = 'LIkptrpdXajmLaJTRHYF'
            email = user.email
            first_name = user.first_name
            last_name = user.last_name
            id_membre = UserProfile.objects.get(user_id=user.id).rpid
            day = '08'
            month = '09'
            year = '2016'

            crypt = hashlib.sha256(id_membre.lower()+api).hexdigest()

            d = hashlib.sha256(date+api).hexdigest()
            dada = hashlib.sha256(datess+api).hexdigest()
            url = 'https://lms.vodeclic.com/api/sso?'

            data_fr = 'partenaire='+partenaire+'&encrypted_id='+crypt+'&id='+id_membre+'&prenom='+first_name+'&nom='+last_name+'&email='+email+'&d='+d+''

            href_sso = url+data_fr

            return href_sso

        else:
            return False
