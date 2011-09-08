.. _settings:

========
Settings
========

POLLIT_SETTINGS
===============

Dictionary of all the Pollit settings

Default::

    DEFAULT_COOKIE_KEY = pollit_ckey

COOKIE_KEY
----------

The key to use when storing/retrieving poll choice data for a user


STATUS_CHOICES
--------------

Used for the choices of `Poll.status`

Default::

    DEFAULT_STATUS_CHOICES = (
        (1, _(u'Controlled By Expire Date')),
        (2, _(u'Open')),
        (3, _(u'Closed'))
    )
    
STATUS_CLOSED_CHOICE
--------------------

The choice to identify when a poll is closed

Default::
    
    DEFAULT_STATUS_CLOSED_CHOICE = 3

STATUS_EXPIRED_BY_DATE_CHOICE
-----------------------------

The choice to identify when to check the expired date for a poll

Default::

    DEFAULT_STATUS_EXPIRED_BY_DATE_CHOICE = 1
    
STATUS_ACTIVE_CHOICE
--------------------

The default choice for active poll's

Default::

    DEFAULT_ACTIVE_CHOICE = 2

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
