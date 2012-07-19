from django.conf import settings
import hashlib
DEFAULT_SETTINGS = {
    'AUTHENTICATION_REQUIRED': True,
    'CHECK_FOR_BOTS':False,
    'POLL_CHOICE_DATA_COOKIE_MAX_AGE':14*24*60*60, # days * hours_in_a_day * minutes_in_an_hour * seconds_in_a_minute
    'COOKIE_DOMAIN':None,
    'COOKIES_ENABLED_KEY':hashlib.sha224('cookies_enabled').hexdigest(),
    'COOKIES_ENABLED_MAX_AGE':365*24*60*60, # days * hours_in_a_day * minutes_in_an_hour * seconds_in_a_minute
}
DEFAULT_SETTINGS.update(getattr(settings, 'POLLIT_SETTINGS', {}))
globals().update(DEFAULT_SETTINGS)