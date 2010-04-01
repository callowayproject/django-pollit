
Getting Started
===============

Download and Install

Add to installed apps

Run syncdb

Adding a poll
=============

::

    from pollit.models import Poll
    
    poll = Poll.objects.create(question="Are you male or female", slug="male_or_female")
