========
Settings
========

POLLIT_SETTINGS
===============

Dictionary of all the Pollit settings


STATUS_CHOICES
--------------

Used for the choices of `Poll.status`

Default::

    DEFAULT_STATUS_CHOICES = (
        (1, _(u'Controlled By Expire Date')),
        (2, _(u'Open')),
        (3, _(u'Closed'))
    )
    
EXPIRED_CHOICE
--------------

The choice to identify when a poll is expired

Default::
    
    DEFAULT_EXPIRED_CHOICE = 3

EXPIRED_BY_DATE_CHOICE
----------------------

The choice to identify when to check the expired date for a poll

Default::

    DEFAULT_EXPIRED_BY_DATE_CHOICE = 1

COMMENT_STATUS_CHOICES
----------------------

Choices to use for showing, disabled or enabled comments

.. note::

    Pollit does not have its own comment system, this is here so you can 
    control the way Pollit should display comments
    
Default::

    DEFAULT_COMMENT_STATUS_CHOICES = (
        (1, _(u'Disabled')),
        (2, _(u'Show Only')),
        (3, _(u'Enabled')),
    )
    
ANONYMOUS_VOTING
----------------

Allow anonymous voting

Default::

    False
