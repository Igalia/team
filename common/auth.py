import base64

from django.conf import settings


def get_user_login(request):
    if settings.USE_BASIC_AUTH:
        return base64.b64decode(request.META['HTTP_AUTHORIZATION'].split()[1]).decode('utf8').split(':')[0]
    return 'average_joe'
