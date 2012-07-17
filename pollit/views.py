"""Request handling code for pollit"""
import datetime
from django.conf import settings
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import Poll, PollChoiceData, PollExpired
from settings import AUTHENTICATION_REQUIRED, CHECK_FOR_BOTS
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
    errors = []
    # If user is logged in and has not voted

    if 'choice' in request.POST and not bot_detection and \
            poll.user_can_vote(request.user, ip):
        try:
            poll.vote(request.POST['choice'], request.user, ip)
            return HttpResponseRedirect(poll.get_absolute_results_url())
        except PollExpired:
            errors.append('The poll has expired.')
    
    poll_choice = poll.get_poll_choice(request.user, ip)
    return render_to_response(template_name,
                              {'poll': poll,
                               'has_voted': (poll_choice is not None),
                               'user_choice': poll_choice,
                               'errors': errors,
                               'must_login_to_vote':AUTHENTICATION_REQUIRED and \
                                        not request.user.is_authenticated()},
                              context_instance=RequestContext(request))

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
    poll_choice = poll.get_poll_choice(request.user, ip)
   
    return render_to_response(template_name,
                              {'poll': poll,
                              'has_voted': poll_choice is not None,
                              'user_choice': poll_choice},
                              context_instance=RequestContext(request))

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
    
