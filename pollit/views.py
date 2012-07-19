"""Request handling code for pollit"""
import datetime
import hashlib
from django.conf import settings
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import Poll, PollExpired
from settings import AUTHENTICATION_REQUIRED, CHECK_FOR_BOTS, \
            POLL_CHOICE_DATA_COOKIE_MAX_AGE, COOKIE_DOMAIN, \
            COOKIES_ENABLED_KEY, COOKIES_ENABLED_MAX_AGE
            
MULTIPLE_SITES = getattr(settings, 'POLLIT_MULTIPLE_SITES', False)

def index(request, count=10, template_name="pollit/index.html"):
    """
    Returns the latest polls, default is 10
    """
    polls = Poll.objects.get_latest_polls(count=count, include_expired=True)
    
    return render_to_response(template_name,
                              {'poll_list': polls},
                              context_instance=RequestContext(request))

def detail_old(request, year, month, slug, template_name="pollit/detail.html"):
    """A backwards-compatible way to handle the old urls"""
    return detail(request, year, month, None, slug, template_name)

def detail(request, year, month, day, slug, template_name="pollit/detail.html"):
    """
    Display the basic voting page. If the user has voted or is not authenticated
    They cannot vote.
    """
    bot_detection = False
    
    # These are bogus fields to try to detect a bot trying to vote. These
    # fields must be added to the form. Look in templates/pollit/detail.html 
    # for example
    if request.POST and CHECK_FOR_BOTS:
        bogus_email = request.POST.get('email', None)
        bogus_username = request.POST.get('username', None)
        if bogus_email != 'valid_email' or bogus_username:
            bot_detection = True

    params = {
        'pub_date__year': year,
        'pub_date__month': datetime.datetime.strptime(month, '%b').month,
        'slug': slug,
    }
    
    if MULTIPLE_SITES:
        params['sites__pk'] = settings.SITE_ID
    if day is not None:
        params['pub_date__day'] = day
    
    try:
        poll = Poll.objects.get(**params)
    except Poll.DoesNotExist, Poll.MultipleItemsReturned:
        raise Http404
    ip = get_client_ip(request)
    poll_choice_data_id = get_poll_choice_id_from_cookies(poll, request.COOKIES)
    
    errors = []
    poll_choice = None
    cookies_enabled = test_cookies_enabled(request.COOKIES)
    
    if 'choice' in request.POST and not bot_detection:
        if cookies_enabled and poll.user_can_vote(request.user, poll_choice_data_id, ip):
            try:
                poll_choice = poll.vote(request.POST['choice'], request.user, 
                                        poll_choice_data_id, ip)
                # This is the same render to response as results. Cannot redirect because
                # we need to set a cookie on the users browser. Plus we already have 
                # everything queried might as well use it
                response = render_to_response('pollit/results.html',
                                  {'poll': poll,
                                  'has_voted': poll_choice is not None,
                                  'user_choice': poll_choice},
                                  context_instance=RequestContext(request))
                response.set_cookie(get_poll_key(poll), poll_choice.id, 
                                    max_age=POLL_CHOICE_DATA_COOKIE_MAX_AGE,
                                    domain=COOKIE_DOMAIN)
                return response
            except PollExpired:
                errors.append('The poll has expired.')
        elif not cookies_enabled:
            errors.append('Cookies must be enabled to vote.')

    poll_choice = poll.get_poll_choice(request.user, poll_choice_data_id, ip)
    
    response = render_to_response(template_name,
                              {'poll': poll,
                               'has_voted': (poll_choice is not None),
                               'user_choice': poll_choice,
                               'errors': errors,
                               'must_login_to_vote':AUTHENTICATION_REQUIRED and \
                                        not request.user.is_authenticated()},
                              context_instance=RequestContext(request))
    add_cookies_enabled_test(response, request.COOKIES)
    return response
    
def results_old(request, year, month, slug, template_name="pollit/results.html"):
    """A backwards-compatible way to handle the old urls"""
    return results(request, year, month, None, slug, template_name)

def results(request, year, month, day, slug, template_name="pollit/results.html"):
    """
    A simple view to show the results on a seperate url
    """
    params = {
        'pub_date__year': year,
        'pub_date__month': datetime.datetime.strptime(month, '%b').month,
        'slug': slug,
    }
    
    if MULTIPLE_SITES:
        params['sites__pk'] = settings.SITE_ID
    if day is not None:
        params['pub_date__day'] = day
    
    try:
        poll = Poll.objects.get(**params)
    except:
        raise Http404
    
    ip = get_client_ip(request)
    poll_choice_id = get_poll_choice_id_from_cookies(poll, request.COOKIES)
    poll_choice = poll.get_poll_choice(request.user, poll_choice_id, ip)
   
    return render_to_response(template_name,
                              {'poll': poll,
                              'has_voted': poll_choice is not None,
                              'user_choice': poll_choice},
                              context_instance=RequestContext(request))

def get_client_ip(request):
    """ Retrieve the client IP """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_poll_choice_id_from_cookies(poll, cookies):
    """ Extract a poll from the cookies. """
    poll_key = get_poll_key(poll)
    poll_choice_data_id = cookies.get(poll_key, None)
    return poll_choice_data_id

def get_poll_key(poll):
    """ Common method for creating what the poll key should be from
    the poll data. Note this should be unique for all polls """
    return hashlib.sha224(poll.get_absolute_url()).hexdigest()

def add_cookies_enabled_test(response, cookies):
    """ Add cookies enabled cookie onto the response, if its not already
    there """
    
    # If authenticaten is required don't do anything
    if AUTHENTICATION_REQUIRED:
        return 
    if not cookies.get(COOKIES_ENABLED_KEY, None):
        response.set_cookie(COOKIES_ENABLED_KEY, 'True', 
                                max_age=COOKIES_ENABLED_MAX_AGE,
                                domain=COOKIE_DOMAIN)
        
def test_cookies_enabled(cookies):
    """ Test to make sure the cookies enabled cookie is set """
    # We know cookies are enabled if they have to be logged in
    if AUTHENTICATION_REQUIRED:
        return True
    return cookies.get(COOKIES_ENABLED_KEY, None) != None