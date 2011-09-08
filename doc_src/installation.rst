
Installation
============

Using PIP::

	pip install django-pollit
	
or download the app `here <http://pypi.python.org/pypi/django-pollit/>`_ ::

	python setup.py install


Add **positions** to your settings **INSTALLED_APPS**::

    INSTALLED_APPS = (
        ...
        'pollit',
        ...
    )
    
Run syncdb::

    >>> ./manage.py syncdb

Add urls::

    urlpatterns = patterns('',
        ...
        (r'^polls/', include('pollit.urls')),
        ...
    )