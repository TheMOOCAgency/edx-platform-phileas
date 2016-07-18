import requests

from django.conf import settings


def recaptcha_verified(request):
    """
    Description: To verify the captcha.

    Request Parameters:
        request object

    Returns:
        Boolean

    Author: Naresh Makwana
    """
    # Set the initial value
    verified = False

    # Get the recaptcha response from the POST
    recaptcha_response = request.POST.get('g-recaptcha-response')

    if recaptcha_response:
        remote_ip = get_remote_ip(request)
        secrete_key = settings.RECAPTCHA_SECRETE_KEY
        try:
            google_response = requests.post(
                settings.RECAPTCHA_VERIFY_ENDPOINT,
                data = {'secret': secrete_key, 'response': recaptcha_response, 'remoteip': remote_ip}
            )
            verified = google_response.json().get('success')
        except:
            pass

    # return verification status
    return verified

def get_remote_ip(request):
    """
    From request object gets the remote IP.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip