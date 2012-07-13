from django.conf import settings

DEFAULT_SETTINGS = {
    'AUTHENTICATION_REQUIRED': True,

   
}
DEFAULT_SETTINGS.update(getattr(settings, 'POLLIT_SETTINGS', {}))
globals().update(DEFAULT_SETTINGS)
