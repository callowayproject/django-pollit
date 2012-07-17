from django.conf import settings

DEFAULT_SETTINGS = {
    'AUTHENTICATION_REQUIRED': True,
    'CHECK_FOR_BOTS':False,
}
DEFAULT_SETTINGS.update(getattr(settings, 'POLLIT_SETTINGS', {}))
globals().update(DEFAULT_SETTINGS)
