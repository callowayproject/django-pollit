from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import warnings

DEFAULT_COOKIE_KEY = "pollit_ckey"

DEFAULT_STATUS_CHOICES = (
    (1, _(u'Controlled By Expire Date')),
    (2, _(u'Open')),
    (3, _(u'Closed'))
)

DEFAULT_STATUS_EXPIRED_BY_DATE_CHOICE = 1
DEFAULT_STATUS_CLOSED_CHOICE = 3
DEFAULT_ACTIVE_CHOICE = 2

DEFAULT_COMMENT_STATUS_CHOICES = (
    (1, _(u'Disabled')),
    (2, _(u'Show Only')),
    (3, _(u'Enabled')),
)

DEFAULT_SETTINGS = {
    'COOKIE_KEY': DEFAULT_COOKIE_KEY,
    'STATUS_CHOICES': DEFAULT_STATUS_CHOICES,
    'STATUS_CLOSED_CHOICE': DEFAULT_STATUS_CLOSED_CHOICE,
    'STATUS_EXPIRED_BY_DATE_CHOICE': DEFAULT_STATUS_EXPIRED_BY_DATE_CHOICE,
    'STATUS_ACTIVE_CHOICE': DEFAULT_ACTIVE_CHOICE,
    'COMMENT_STATUS_CHOICES': DEFAULT_COMMENT_STATUS_CHOICES,
    'ANONYMOUS_VOTING': False
}

error_str = "settings.%s is deprecated; use settings.POLLIT_SETTINGS instead."

USER_SETTINGS = getattr(settings, 'POLLIT_SETTINGS', {})

DEFAULT_SETTINGS.update(USER_SETTINGS)
    
globals().update(DEFAULT_SETTINGS)