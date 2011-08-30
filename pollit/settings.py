from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import warnings

DEFAULT_STATUS_CHOICES = (
    (1, _(u'Controlled By Expire Date')),
    (2, _(u'Open')),
    (3, _(u'Closed'))
)

DEFAULT_EXPIRED_BY_DATE_CHOICE = 1
DEFAULT_EXPIRED_CHOICE = 3

DEFAULT_COMMENT_STATUS_CHOICES = (
    (1, _(u'Disabled')),
    (2, _(u'Show Only')),
    (3, _(u'Enabled')),
)

DEFAULT_SETTINGS = {
    'STATUS_CHOICES': DEFAULT_STATUS_CHOICES,
    'EXPIRED_CHOICE': DEFAULT_EXPIRED_CHOICE,
    'EXPIRED_BY_DATE_CHOICE': DEFAULT_EXPIRED_BY_DATE_CHOICE,
    'COMMENT_STATUS_CHOICES': DEFAULT_COMMENT_STATUS_CHOICES,
    'ANONYMOUS_VOTING': False
}

error_str = "settings.%s is deprecated; use settings.POLLIT_SETTINGS instead."

USER_SETTINGS = getattr(settings, 'POLLIT_SETTINGS', {})

DEFAULT_SETTINGS.update(USER_SETTINGS)
    
globals().update(DEFAULT_SETTINGS)